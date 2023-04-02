import random

# define tuple space
tuple_space = []

# define function for adding new item to the tuple space
def add_item(name, price):
    item = (name, price)
    tuple_space.append(item)
    print(f"New item added: {item}")
    
# define function for searching item by name in the tuple space
def search_item(name):
    result = []
    for item in tuple_space:
        if item[0] == name:
            result.append(item)
    if len(result) > 0:
        print(f"Item(s) found with name '{name}':")
        for item in result:
            print(f"- {item}")
    else:
        print(f"No item found with name '{name}'")
            
# define function for purchasing item by name from the tuple space
def purchase_item(name):
    result = []
    for item in tuple_space:
        if item[0] == name:
            result.append(item)
    if len(result) > 0:
        item = random.choice(result)
        tuple_space.remove(item)
        print(f"Item purchased: {item}")
    else:
        print(f"No item found with name '{name}'")

# # add new items to tuple space
# add_item("Shirt", 10000)
# add_item("Pants", 20000)
# add_item("Shoes", 50000)

# # search for an item in tuple space
# search_item("Shirt")

# # purchase an item from tuple space
# purchase_item("Shoes")
