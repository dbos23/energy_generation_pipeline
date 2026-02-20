use schema {{ schema }};

--------------------
--set up stage


--connect snowflake with s3
create storage integration eia_storage_integration
    type = external_stage
    storage_provider = s3
    enabled = true
    storage_aws_role_arn = '{{ aws_role_arn }}'
    storage_allowed_locations = ('{{ aws_bucket_url }}')
;

--storage_aws_iam_user_arn and storage_aws_external_id need to be copied into the trust relationship for the role in AWS
desc integration eia_storage_integration;

--stage data from s3
create or replace stage energy_generation
    url = '{{ aws_bucket_url }}'
    storage_integration = eia_storage_integration
    file_format = (
        type = 'JSON'
        strip_outer_array = true
);

--view all files in the s3 bucket to confirm storage integration is working properly
list @energy_generation;





--------------------
--set up tables and stream


--create raw table
create table eia_raw (
  json_data variant,
  file_name varchar
);

--create a stream to use to process only newly added data
create stream eia_stream
on table eia_raw
;

--create fact table
create table fct_energy_outputs (
    period date,
    fuel_type_code varchar,
    fuel_type_name varchar,
    respondent_code varchar,
    respondent_name varchar,
    timezone varchar,
    timezone_description varchar,
    amount_generated int,
    units varchar
);





--------------------
--automate ingestion of files from S3 to raw table


--create task to read files from stage and copy their data into the raw table
create or replace task ingest_eia_files
warehouse = dataschool_wh
schedule = 'using cron 25 16 * * * UTC' --runs at 4:25pm UTC / 11:25am Eastern
as
    --insert new files from stage into raw table
    copy into eia_raw
    from (
        select
            $1,
            metadata$filename
        from @energy_generation
    )
    file_format = (
        type = 'JSON',
        strip_outer_array = true
);

--activate task
alter task ingest_eia_files resume;





--------------------
--atuomate the refresh of fct_energy_outputs and monthly_energy_generation


--create stored procedure to refresh all tables
create or replace procedure refresh_eia()
returns varchar
language sql
as
$$
begin

--------------------

insert into fct_energy_outputs (
    select
        value:period::date as period,
        value:fueltype::varchar as fuel_type_code,
        value:"type-name"::varchar as fuel_type_name,
        value:respondent::varchar as respondent_code,
        value:"respondent-name"::varchar as respondent_name,
        value:timezone::varchar as timezone,
        value:"timezone-description"::varchar as timezone_description,
        value:value::int as amount_generated,
        value:"value-units"::varchar as units,
    from eia_stream,
        lateral flatten(input => json_data:response:data)
);

--------------------

create or replace table monthly_energy_generation as (
    select
        date_trunc('month', period) as month,
        fuel_type_code,
        fuel_type_name,
        respondent_code,
        respondent_name,
        units,
        sum(amount_generated) as amount_generated
    from fct_energy_outputs
    group by all
    order by
        month asc,
        amount_generated desc
);

return 'All tables updated';

end;
$$;

--create task to run the stored procedure after the files have been ingested into the raw table (checking if the stream has data so as not to run unnecessarily)
create or replace task run_eia_pipeline
warehouse = {{ warehouse }}
after ingest_eia_files
when system$stream_has_data('eia_stream')
as
call refresh_eia()
;

--activate task
alter task run_eia_pipeline resume;