def get_content_type(file_name):
    if file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
        return 'image/jpeg'
    elif file_name.endswith('.png'):
        return 'image/png'
    elif file_name.endswith('.gif'):
        return 'image/gif'
    return 'application/octet-stream'
