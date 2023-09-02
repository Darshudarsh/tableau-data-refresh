import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node Read from S3 bucket
ReadfromS3bucket_node1 = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "multiline": True,
        "optimizePerformance": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={
        "paths": ["s3://snowflake-s3-darshini/load/mytable.csv"],
        "recurse": True,
    },
    transformation_ctx="ReadfromS3bucket_node1",
)

# Script generated for node Transformation
Transformation_node2 = ApplyMapping.apply(
    frame=ReadfromS3bucket_node1,
    mappings=[
        ("C_CUSTOMER_ID", "string", "C_CUSTOMER_ID", "varchar"),
        ("C_EMAIL_ADDRESS", "string", "C_EMAIL_ADDRESS", "string"),
    ],
    transformation_ctx="Transformation_node2",
)

# Script generated for node Write to Snowflake
WritetoSnowflake_node3 = glueContext.write_dynamic_frame.from_options(
    frame=Transformation_node2,
    connection_type="marketplace.spark",
    connection_options={
        "sfUrl": "vqlxhjj-ed20890.snowflakecomputing.com",
        "sfWarehouse": "COMPUTE_WH",
        "dbtable": "mytable",
        "sfDatabase": "mydb",
        "sfSchema": "myschema",
        "connectionName": "snowflake-connection",
    },
    transformation_ctx="WritetoSnowflake_node3",
)

job.commit()
