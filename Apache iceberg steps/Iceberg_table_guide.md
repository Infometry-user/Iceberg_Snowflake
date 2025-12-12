
**Implementation Guide: Snowflake Iceberg Tables and External Volumes on AWS**

**Executive Summary**

This document outlines the step-by-step procedure for configuring Snowflake Iceberg tables using an AWS S3 bucket as the storage backend. It covers the necessary AWS IAM configurations, Snowflake Storage Integrations, External Volume creation, and the execution of DDL and DML operations to manage Iceberg data.

<img src="Iceberg%20table%20guide_html_546e56df.gif" id="Shape1" data-align="bottom" width="602" height="2" alt="Shape1" />

  

**Prerequisites to setup AWS and Snowflake Account**

Before proceeding, ensure you have active accounts for both Snowflake and AWS. If you already have these accounts, please log in to your respective management consoles. If not, you can create them using the links below:

**Snowflake:** <u>[Click here to create Snowflake trail account](https://signup.snowflake.com/?utm_source=google&utm_medium=paidsearch&utm_campaign=ap-in-en-brand-trial-exact&utm_content=go-eta-evg-ss-free-trial&utm_term=c-g-snowflake%20trial-e&_bt=579374819453&_bk=snowflake%20trial&_bm=e&_bn=g&_bg=133380618168&gclsrc=aw.ds&gad_source=1&gad_campaignid=14804341907&gbraid=0AAAAADCzRJV4S_x7OOmV4WnzotydXOZs0&gclid=Cj0KCQiA9OnJBhD-ARIsAPV51xP4d21ZTO3QMwGiBAeWxZs0naeauBYJF-Nv9mOeTmNQ-EV8OGRDLCUaAsIPEALw_wcB)</u>

**AWS:** <u>[Click here to create AWS trail account](https://signin.aws.amazon.com/signup?request_type=register)</u>

**1. AWS Configuration Prerequisites**

To support Snowflake Iceberg tables, the S3 bucket must be located in the same region that hosts the Snowflake account.

**Step 1: Create IAM Policy**

This policy gives Snowflake the minimum S3 permissions it needs: listing the bucket, discovering its region, and reading/writing/deleting objects in a specific bucket path. These scoped permissions follow least-privilege principles, so Snowflake cannot access other buckets or prefixes beyond what you explicitly allow.

Configure an access policy to allow Snowflake to interact with the specific S3 bucket (your_bucket_name).

1.  Log into the AWS Management Console and navigate to **IAM \> Policies \> Create policy**.

2.  Select the JSON tab and enter the following policy content:

```JSON
{
"Version": "2012-10-17",
"Statement": [
{
"Effect": "Allow",
"Action": [
"s3:ListBucket",
"s3:GetBucketLocation"
],
"Resource": "arn:aws:s3:::<your_bucket_name>"
},
{
"Effect": "Allow",
"Action": [
"s3:GetObject",
"s3:PutObject",
"s3:DeleteObject"
],
"Resource": "arn:aws:s3:::<your_bucket_name>"
}
]
}
```
  

3.  Name the policy (e.g., snowflake_Iceberg_Policy) and create it.

**Step 2: Create IAM Role and Trust Relationship**

The IAM role is the security identity that Snowflake assumes when accessing your S3 bucket, instead of using long‑lived access keys. The trust relationship ensures that only the specific Snowflake IAM principal with the correct external ID can assume this role, preventing other AWS accounts from misusing it.

Create an IAM role that Snowflake will assume to access the data.

1.  Navigate to **IAM \> Roles \> Create role**.

2.  Select **Trusted entity type** as **AWS account**.

3.  Select **Another AWS account** and specify your AWS account ID temporarily.

4.  Select the **Require external ID** option and enter a placeholder ID (e.g., 0000 or external_icerberg).

<img src="Iceberg%20table%20guide_html_d3306bf0.png" id="Picture 17" data-align="bottom" data-border="0" width="602" height="476" />

5.  After creating the role (iceberg_role), update the **Trust Relationship** with the specific Snowflake IAM user and External ID.

<img src="Iceberg%20table%20guide_html_b8606c54.png" id="Picture 15" data-align="bottom" data-border="0" width="519" height="293" />

**Trust Relationship JSON:**

  

```JSON
{
"Version": "2012-10-17",
"Statement": [
{
"Effect": "Allow",
"Principal": {
"AWS": "arn:aws:iam::719084987142:user/2f9a1000-s"
},
"Action": "sts:AssumeRole",
"Condition": {
"StringEquals": {
"sts:ExternalId": "WQ81422_SFCRole=6_yA5e+WIE7KTwpxpe36Rj6/cFnyo="

}

}

}

]

}
```
  

  

  

<img src="Iceberg%20table%20guide_html_ee5f694e.png" id="Picture 16" data-align="bottom" data-border="0" width="618" height="297" />

  

<img src="Iceberg%20table%20guide_html_546e56df.gif" id="Shape2" data-align="bottom" width="602" height="2" alt="Shape2" />

**2. Snowflake Storage Configuration**

Create an external volume that points to the S3 bucket and prefix where Iceberg table data and metadata will be stored. In the external volume definition, reference the IAM role ARN and external ID so Snowflake can access S3 securely without embedding AWS keys in SQL.​

**Step 1: Create External Volume**

The External Volume defines the storage location for Iceberg tables.
```sql   
CREATE OR REPLACE EXTERNAL VOLUME iceberg_snf_demo_ext_vol
STORAGE_LOCATIONS =
(
(
NAME = 'snf_ext_volume_s3'
STORAGE_PROVIDER = 'S3'
<span id="_GoBack"><span> STORAGE_BASE_URL = 's3://<your_bucket_name><your_folder_name1>'
STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::729442710163:role/iceberg_role'
STORAGE_AWS_EXTERNAL_ID = 'WQ81422_SFCRole=6_yA5e+WIE7KTwpxpe36Rj6/cFnyo='
)
)
ALLOW_WRITES = TRUE;
```

  

**Verification:**

Describe the external volume to ensure the storage locations, role ARN, and write permissions are correctly configured. Successful verification confirms that Snowflake can use this volume as the storage backend for Iceberg tables.

  
  
```sql
DESC EXTERNAL VOLUME iceberg_snf_demo_ext_vol;
```
  

  

<img src="Iceberg%20table%20guide_html_546e56df.gif" id="Shape3" data-align="bottom" width="602" height="2" alt="Shape3" />

**3. Iceberg Table Implementation**

**Step 1: Create Iceberg Table**

Initialize the Iceberg table using the previously created External Volume ('ICEBERG_SNF_DEMO_EXT_VOL') and define the catalog as SNOWFLAKE.
```sql
CREATE OR REPLACE ICEBERG TABLE ICERBERG_CUSTOMERS (
"ORDER_ID" TEXT,
"CUSTOMER_ID" TEXT,
"ORDER_DATE" DATE,
"PRODUCT_ID" TEXT,
"QUANTITY" NUMBER(2, 0),
"TOTAL_AMOUNT" NUMBER(6, 1)
)
EXTERNAL_VOLUME = 'ICEBERG_SNF_DEMO_EXT_VOL'
CATALOG = 'SNOWFLAKE';
```

  

**Step 2: Load Data**

  
```sql
INSERT INTO ICEBERG_CUSTOMERS ("ORDER_ID", "CUSTOMER_ID", "ORDER_DATE", "PRODUCT_ID", "QUANTITY", "TOTAL_AMOUNT")
VALUES
('O000001', 'C00151', '2024-06-01', 'P00103', 4, 80.0),
('O000002', 'C00160', '2025-08-14', 'P00071', 3, 93.0),
('O000003', 'C00028', '2024-04-30', 'P00066', 10, 420.0),
('O000004', 'C00062', '2024-02-01', 'P00057', 5, 90.0),
('O000005', 'C00028', '2024-12-12', 'P00028', 4, 940.0),
('O000006', 'C00128', '2025-03-22', 'P00119', 9, 864.0),
('O000007', 'C00190', '2024-10-27', 'P00097', 1, 90.0),
('O000008', 'C00027', '2024-02-19', 'P00062', 9, 369.0),
('O000009', 'C00003', '2024-08-09', 'P00103', 6, 120.0),
('O000010', 'C00155', '2025-03-28', 'P00009', 5, 4165.0),
('O000011', 'C00051', '2024-10-30', 'P00106', 8, 56.0),
('O000012', 'C00160', '2025-03-20', 'P00096', 8, 424.0),
('O000013', 'C00180', '2024-08-23', 'P00113', 1, 70.0),
('O000014', 'C00052', '2024-10-18', 'P00012', 7, 6608.0),
('O000015', 'C00131', '2024-02-22', 'P00113', 5, 350.0),
('O000016', 'C00184', '2025-11-06', 'P00081', 1, 350.0),
('O000017', 'C00130', '2025-03-28', 'P00092', 6, 306.0),
('O000018', 'C00129', '2025-09-16', 'P00019', 2, 1606.0),
('O000019', 'C00172', '2024-09-18', 'P00090', 6, 1812.0),
('O000020', 'C00068', '2025-07-08', 'P00055', 8, 1080.0);
```

  

**Verify Iceberg Data:**

  
  
```sql
SELECT * FROM ICEBERG_CUSTOMERS;
```

  

  

  

<img src="Iceberg%20table%20guide_html_9dab4e1d.png" id="Picture 12" data-align="bottom" data-border="0" width="602" height="211" />

<img src="Iceberg%20table%20guide_html_546e56df.gif" id="Shape4" data-align="bottom" width="602" height="2" alt="Shape4" />

**5. DML Operations and Testing**

The following SQL commands validate the Iceberg table's ability to handle transactional operations (INSERT, UPDATE, DELETE).

**Insert Records**

```sql
INSERT INTO ICEBERG_CUSTOMERS ("ORDER_ID", "CUSTOMER_ID", "ORDER_DATE", "PRODUCT_ID", "QUANTITY", "TOTAL_AMOUNT")
VALUES (
'O999001',
'C99901',
'2025-12-01',
'P99901',
2,
150.0
);
```

```sql
INSERT INTO ICEBERG_CUSTOMERS ("ORDER_ID", "CUSTOMER_ID", "ORDER_DATE", "PRODUCT_ID", "QUANTITY", "TOTAL_AMOUNT")
VALUES (
'O999002',
'C99902',
'2025-12-02',
'P99902',
5,
500.5
);
```

  

<img src="Iceberg%20table%20guide_html_cbcd3212.png" id="Picture 1" data-align="bottom" data-border="0" width="602" height="176" />

**Update Records**

  
  
```sql
UPDATE ICEBERG_CUSTOMERS
SET
"QUANTITY" = 10,
"TOTAL_AMOUNT" = 200.0
WHERE
"ORDER_ID" = 'O000001';
```

  

  

Before updating

  

<img src="Iceberg%20table%20guide_html_e6d76ca2.png" id="Picture 14" data-align="bottom" data-border="0" width="653" height="100" />

  

After updating  
  
<img src="Iceberg%20table%20guide_html_977e143e.png" id="Picture 13" data-align="bottom" data-border="0" width="602" height="139" />

**Delete Records**

  
  
```sql
DELETE FROM ICEBERG_CUSTOMERS
WHERE "ORDER_ID" = 'O000002';
```
  

  

Before deleting  
  
<img src="Iceberg%20table%20guide_html_8cabba86.png" id="Image2" data-align="bottom" data-border="0" width="601" height="96" />

  

After deleting

  

<img src="Iceberg%20table%20guide_html_17960b8.png" id="Picture 11" data-align="bottom" data-border="0" width="602" height="131" />

  

  

  

  
