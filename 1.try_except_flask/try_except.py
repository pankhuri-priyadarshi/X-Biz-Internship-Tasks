from flask import Flask

app = Flask(__name__)

# 1. ZeroDivisionError
@app.route('/divide')
def divide():
    try:
        result = 10 / 0
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Cannot divide by zero!"

# 2. ValueError - wrong type conversion
@app.route('/valueerror')
def value_error():
    try:
        num = int("abc")
        return str(num)
    except ValueError:
        return "Invalid number format!"

# 3. TypeError - unsupported operation
@app.route('/typeerror')
def type_error():
    try:
        result = "hello" + 5
        return str(result)
    except TypeError:
        return "Cannot add string and integer!"

# 4. KeyError
@app.route('/keyerror')
def key_error():
    data = {"name": "Pankhuri"}
    try:
        return data["age"]
    except KeyError:
        return "Key not found in dictionary!"

# 5. IndexError
@app.route('/indexerror')
def index_error():
    numbers = [1, 2, 3]
    try:
        return str(numbers[5])
    except IndexError:
        return "Index is out of range!"

# 6. FileNotFoundError
@app.route('/fileerror')
def file_error():
    try:
        f = open("not_exist.txt", "r")
        return f.read()
    except FileNotFoundError:
        return "File does not exist!"

# 7. ModuleNotFoundError
@app.route('/moduleerror')
def module_error():
    try:
        import notamodule
    except ModuleNotFoundError:
        return "Module not found!"

# 8. AttributeError 
@app.route('/attributeerror')
def attribute_error():
    try:
        x = 10
        x.append(5)
        return str(x)
    except AttributeError:
        return "Object has no such attribute!"

# 9. NameError
@app.route('/nameerror')
def name_error():
    try:
        return str(abc)
    except NameError:
        return "NameError: Variable not defined!"


# 10. PermissionError
@app.route('/permissionerror')
def permission_error():
    try:
        f = open("/system/secret.txt", "w")
        return f.write("test")
    except PermissionError:
        return "PermissionError: Permission denied!"

# 11. MemoryError
@app.route('/memoryerror')
def memory_error():
    try:
        big_list = [1] * (10**10)  # Huge list, likely to crash RAM
        return f"List created with length {len(big_list)}"
    except MemoryError:
        return "MemoryError: Not enough memory to handle this operation!"


# 12. ImportError
@app.route('/importerror')
def import_error():
    try:
        from math import cube
        return str(cube(3))
    except ImportError:
        return "ImportError: Function not found in module!"


# 13. RuntimeError
@app.route('/runtimeerror')
def runtime_error():
    import sys
    sys.setrecursionlimit(5)

    try:
        def test():
            test()
        test()
    except RuntimeError as e:
        return f"RuntimeError: {str(e)}"


@app.route('/runtimeerror2')
def runtime_error2():
    try:
        def my_gen():
            yield 1
            yield 2

        g = my_gen()
        next(g)
        g.send(10) 
    except RuntimeError as e:
        return f"RuntimeError: {str(e)}"
    
# 14. AssertionError
@app.route('/assertionerror')
def assertion_error():
    try:
        x = 5
        assert x > 10 
        return "Assertion passed!"
    except AssertionError:
        return "Assertion failed!"

@app.route('/check_age/<int:age>')
def check_age(age):
    try:
        assert age >= 18, "Age must be 18 or older"
        return f" Your age is {age}"
    
    except AssertionError as e:
        return f"AssertionError: {str(e)}"

# 15. Generic Exception
@app.route('/genericerror')
def generic_error():
    try:
        y = "abc" / 5
        return str(y)
    except Exception as e:
        return f"Caught a generic error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
