print("Importing rembg...")
try:
    from rembg import remove, new_session
    print("Imported rembg.")
    s = new_session()
    print("Session created.")
except Exception as e:
    print(f"Error: {e}")
