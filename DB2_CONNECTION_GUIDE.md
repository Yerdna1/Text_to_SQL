# 🏢 IBM DB2 Connection Guide

## Prerequisites

### 1. Install IBM DB2 Driver

```bash
# Install the IBM DB2 Python driver
pip install ibm-db

# Alternative: Install with conda
conda install -c conda-forge ibm-db
```

### 2. DB2 Connection Information Needed

You'll need the following information from your DB2 administrator:

- **Hostname**: DB2 server hostname (e.g., `db2server.company.com`)
- **Port**: Usually `50000` for DB2 (default)
- **Database**: Database name (e.g., `PROD`, `SAMPLE`)
- **Username**: Your DB2 username
- **Password**: Your DB2 password
- **SSL**: Whether to use SSL connection (recommended: Yes)

## Connection Steps

### 1. Open Application
Navigate to the sidebar and find the **"🗄️ Database Connection"** section.

### 2. Expand "🔧 Connect to IBM DB2"
Click to expand the DB2 connection form.

### 3. Fill Connection Details
- **Hostname**: Your DB2 server hostname
- **Port**: Usually 50000
- **Database**: Your database name
- **Username**: Your DB2 username
- **Password**: Your DB2 password
- **Use SSL**: ✅ Recommended for security

### 4. Click "🔌 Connect to DB2"
The application will:
- Test the connection
- Automatically discover MQT tables
- Load schema information
- Display connection status

## Expected DB2 Tables

The application looks for IBM Sales Pipeline MQT tables:

### Core Tables:
- `PROD_MQT_CONSULTING_PIPELINE`
- `PROD_MQT_CONSULTING_BUDGET`
- `PROD_MQT_CONSULTING_REVENUE_ACTUALS`
- `PROD_MQT_SW_SAAS_OPPORTUNITY`
- `PROD_MQT_SOFTWARE_TRANSACTIONAL_PIPELINE`

### Schema Discovery:
The application automatically queries:
```sql
SELECT TABSCHEMA, TABNAME, TYPE 
FROM SYSCAT.TABLES 
WHERE TABNAME LIKE '%MQT%' 
   OR TABNAME LIKE 'PROD_MQT%'
```

## Troubleshooting

### ❌ "IBM DB2 Driver Missing"
**Solution**: Install the driver
```bash
pip install ibm-db
```

### ❌ "Connection Error"
**Possible Causes**:
1. **Network**: Firewall blocking port 50000
2. **Credentials**: Wrong username/password
3. **Hostname**: Incorrect server address
4. **SSL**: Try toggling SSL on/off
5. **VPN**: May need VPN connection to corporate network

### ❌ "No MQT Tables Found"
**Solutions**:
1. Check if you have permissions to the tables
2. Verify table names with your DB2 administrator
3. Tables might be in a different schema

### 🔧 Test Connection Manually
You can test the connection outside the app:

```python
import ibm_db

# Replace with your actual connection details
conn_str = "DATABASE=SAMPLE;HOSTNAME=your-server.com;PORT=50000;PROTOCOL=TCPIP;UID=username;PWD=password;Security=SSL;"

try:
    conn = ibm_db.connect(conn_str, "", "")
    print("✅ Connection successful!")
    ibm_db.close(conn)
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

## Security Notes

1. **SSL Recommended**: Always use SSL in production
2. **Credentials**: Never hardcode credentials in code
3. **Network**: Use VPN for external connections
4. **Permissions**: Follow principle of least privilege

## Once Connected

When successfully connected to DB2:
- ✅ Status shows "🏢 Connected: IBM DB2 Database"
- ✅ Schema information automatically loaded
- ✅ All SQL queries use pure DB2 syntax
- ✅ `FETCH FIRST n ROWS ONLY` works correctly
- ✅ `DECIMAL(value, precision, scale)` functions work
- ✅ DB2 date functions work: `YEAR(CURRENT DATE)`

## Support

If you need help:
1. Contact your DB2 database administrator
2. Check IBM DB2 documentation
3. Verify network connectivity and permissions