class Config:
    SECRET_KEY = '8844685d1a027f0c24bfcb59'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Heigbaunhf22@localhost/check_querry'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 600,
    }

    # slack
    SLACK_TOKEN = 'xoxb-22279762672-5669602083767-9nSwGd14LQQWcOijTm6Jh7fB'
    SLACK_CHANNEL_ID = 'C05L3APK4V8'
    SLACK_TOKEN_AUTH = 'Bearer xoxb-22279762672-5669602083767-9nSwGd14LQQWcOijTm6Jh7fB'

    # email details
    email = 'noreply@apentis.eu'
    password = 'nG9NU<Qu2'

    # ssh
    private_key_path = r'/Users/hugolemonnier/Desktop/id_rsa'
    file_path_on_server = r"F:\application\scripts\sql_file_executor\query_tool_script.sql"
    command = f'go run F:\\application\\scripts\\sql_file_executor\\sql_file_executor.go query_tool Apentis2023'

    #decrypt key
    decryption_keys = {
        'TEST': '8RKtW5$$H%^&nE*G',
        'PROD LU': '0QuaSKHWJ8dVjr8M',
        'PROD CH': '0QuaSKHWJ8dVjr8M'
    }