import uuid, re

def generate_task_id():
    return f"task_{uuid.uuid4().hex[:8]}"

def generate_session_id():
    return f"session_{uuid.uuid4().hex[:12]}"

def generate_uuid():
    return str(uuid.uuid4())

def sanitize_filename(filename):
    return re.sub(r'[^\w\-_\. ]', '', filename).replace(' ', '_')
