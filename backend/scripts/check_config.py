import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SECRET_KEY'))
result = (
    client.table('avatar_config')
    .select('*')
    .eq('user_id', 'test_user_001')
    .eq('avatar_id', 'test_avatar_001')
    .limit(1)
    .execute()
)
print('DATA:', result.data)