def get_permission_from_user(prompt_msg: str) -> bool:
    user_permission = ''
    while not user_permission in ['y', 'n']:
        user_permission = input(f"{prompt_msg} (y/n) ").lower()
    
    return user_permission == 'y'
