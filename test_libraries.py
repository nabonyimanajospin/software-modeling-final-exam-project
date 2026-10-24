print("🧪 Testing if all libraries are installed...\n")

try:
    import flask
    print("✅ flask - INSTALLED")
except:
    print("❌ flask - NOT INSTALLED")

try:
    import flask_login
    print("✅ flask-login - INSTALLED")
except:
    print("❌ flask-login - NOT INSTALLED")

try:
    import flask_sqlalchemy
    print("✅ flask-sqlalchemy - INSTALLED")
except:
    print("❌ flask-sqlalchemy - NOT INSTALLED")

try:
    import werkzeug
    print("✅ werkzeug - INSTALLED")
except:
    print("❌ werkzeug - NOT INSTALLED")

try:
    from PIL import Image
    print("✅ pillow - INSTALLED")
except:
    print("❌ pillow - NOT INSTALLED")

try:
    import reportlab
    print("✅ reportlab - INSTALLED")
except:
    print("❌ reportlab - NOT INSTALLED")

try:
    import pandas
    print("✅ pandas - INSTALLED")
except:
    print("❌ pandas - NOT INSTALLED")

try:
    import matplotlib
    print("✅ matplotlib - INSTALLED")
except:
    print("❌ matplotlib - NOT INSTALLED")

print("\n" + "="*50)
print("✅ If you see ALL ✅ above, you're ready!")
print("="*50)