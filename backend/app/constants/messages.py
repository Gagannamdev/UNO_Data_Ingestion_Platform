class SuccessMessages:
    API_RUNNING = "UNO Data Ingestion Platform API is running"

    DATABASE_CONNECTED = "MongoDB Atlas connected successfully"
    DATABASE_DISCONNECTED = "MongoDB Atlas connection closed"

    USER_CREATED = "User created successfully"
    USERS_FETCHED = "Users fetched successfully"
    LOGIN_SUCCESS = "Login successful"

    CONNECTION_CREATED = "Connection created successfully"
    CONNECTION_UPDATED = "Connection updated successfully"
    CONNECTION_DELETED = "Connection deleted successfully"
    CONNECTION_TEST_SUCCESS = "Connection tested successfully"

    CONNECTION_OBJECTS_FETCHED = (
        "Connection objects fetched successfully"
    )

    CONNECTION_PREVIEW_FETCHED = (
        "Preview data fetched successfully"
    )

    PIPELINE_CREATED = "Pipeline created successfully"
    PIPELINES_FETCHED = "Pipelines fetched successfully"
    PIPELINE_FETCHED = "Pipeline fetched successfully"
    PIPELINE_UPDATED = "Pipeline updated successfully"
    PIPELINE_DELETED = "Pipeline deleted successfully"

    PIPELINE_VALIDATED = (
        "Pipeline configuration validated successfully"
    )
    PIPELINE_PREVIEW_FETCHED = (
    "Pipeline preview generated successfully"
    )






class ErrorMessages:
    INTERNAL_SERVER_ERROR = (
        "An unexpected internal server error occurred"
    )

    DATABASE_CONNECTION_FAILED = (
        "Unable to connect to the database"
    )

    DATABASE_OPERATION_FAILED = "Database operation failed"
    TRANSACTION_FAILED = "Database transaction failed"

    UNAUTHORIZED = "Authentication is required"
    INVALID_TOKEN = "Invalid or expired authentication token"
    INVALID_CREDENTIALS = "Invalid email or password"

    FORBIDDEN = (
        "You do not have permission to perform this action"
    )

    RESOURCE_NOT_FOUND = "Requested resource was not found"

    USER_NOT_FOUND = "User not found"

    EMAIL_ALREADY_EXISTS = (
        "A user with this email already exists"
    )

    VALIDATION_FAILED = "Request validation failed"

    INVALID_NAME = "Name must contain only valid characters"

    WEAK_PASSWORD = (
        "Password must contain uppercase, lowercase, "
        "number and special character"
    )

    ADMIN_CREATION_NOT_ALLOWED = (
        "Admin users cannot be created through this API"
    )

    CONNECTION_NOT_FOUND = "Connection not found"

    CONNECTION_NAME_EXISTS = (
        "Connection name already exists"
    )

    INVALID_CONNECTION_CONFIG = (
        "Invalid connection configuration"
    )

    INVALID_PORT = (
        "Port must be between 1 and 65535"
    )

    CONNECTION_TEST_FAILED = (
        "Unable to connect using the provided configuration"
    )

    INVALID_CONNECTION_ACTION = (
        "Unsupported connection action"
    )

    CONNECTION_OBJECT_FETCH_FAILED = (
        "Unable to fetch database objects"
    )

    CONNECTION_PREVIEW_FAILED = (
        "Unable to preview data"
    )

    PIPELINE_NOT_FOUND = "Pipeline not found"

    PIPELINE_NAME_EXISTS = (
        "A pipeline with this name already exists"
    )

    INVALID_PIPELINE_CONFIG = (
        "Invalid pipeline configuration"
    )

    SQL_QUERY_REQUIRED = (
        "SQL transformation query is required"
    )

    INVALID_SQL_QUERY = (
        "Only SELECT or WITH queries are allowed"
    )

    UNSAFE_SQL_QUERY = (
        "SQL query contains a restricted operation"
    )

    MULTIPLE_SQL_STATEMENTS = (
        "Multiple SQL statements are not allowed"
    )

    CRON_REQUIRED = (
        "Cron expression is required when schedule is enabled"
    )

    INVALID_CRON = (
        "Invalid cron expression"
    )

    SPARK_START_FAILED = (
        "Unable to start the Spark engine"
    )

    NO_SOURCE_DATA = (
        "Source data is required for transformation"
    )

    SPARK_DATAFRAME_FAILED = (
        "Unable to create Spark DataFrame"
    )

    TRANSFORMATION_FAILED = (
        "Transformation query execution failed"
    )
    PIPELINE_PREVIEW_FAILED = (
    "Unable to generate pipeline preview"
    )




