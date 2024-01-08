import prestapyt
import os
import json
import re
import requests
import xmltodict
import random
import io

LINK = "http://localhost:8080/api/"
SCRIPT_DIR = "../"
API_KEY = "IU32CED438GDI67NQVDJJFDE9EFWVGEC"

def add_category(name: str, parent_id: int) -> int:
    category = prestashop.get("categories", options={
        "filter[name]": name
    })
      
    category_schema["category"]["name"]["language"]["value"] = name
    category_schema["category"]["id_parent"] = parent_id
    category_schema["category"]["active"] = 1
    category_schema["category"]["link_rewrite"]["language"]["value"] = re.sub(
        r"[^a-zA-Z0-9]+", "-", name).lower()
    category_schema["category"]["description"][
        "language"]["value"] = f"Kategoria {name}"
    print("Category added..." + name)
    return prestashop.add("categories", category_schema)["prestashop"]["category"]["id"]

# important - on the nbsklep.pl there are: main_category/sub_category/sub_sub_category
# there is a problem: meski/obuwie/biegowe and damski/obuwie/biegowe - "obuwie" from "meski" and "obuwie" from "damski" are different categories, not the same (the same with "biegowe")  
# this function checks and picks proper category when such naming problem occurs 
def get_product_categories(product: dict) -> (int, int, int): 
     # MAIN CATEGORY
    main_category= prestashop.get("categories", options={
        "filter[name]": product.get("Category")
    })
    main_category_id = main_category['categories']['category']['attrs']['id']
    # get full info about main category
    main_category_xml = requests.get(f'{LINK}/categories/{main_category_id}&ws_key={API_KEY}')
    # convert xml response to json
    main_category_props_json = xmltodict.parse(main_category_xml.text)
    # check which categories can be the sub category of main category 
    available_sub_categories= set()
    for available_sub_category in main_category_props_json['prestashop']['category']['associations']['categories']['category']:
        available_sub_categories.add(available_sub_category['id'])
    
    # SUB CATEGORY
    # get all sub_categories 
    sub_category= prestashop.get("categories", options={
        "filter[name]": product.get("Sub_category")
    })
    sub_category_id = 0
    # check which sub category is sub category for our main category
    for single_sub_category in sub_category['categories']['category']:
        if single_sub_category['attrs']['id'] in available_sub_categories:
            sub_category_id = single_sub_category['attrs']['id']
    
    sub_category_xml = requests.get(f'{LINK}/categories/{sub_category_id}&ws_key={API_KEY}')
    # convert xml response to json
    sub_category_props_json = xmltodict.parse(sub_category_xml.text)
    # check which categories can be the sub sub category of sub category 
    available_sub_sub_categories = set()
    for available_sub_sub_category in sub_category_props_json['prestashop']['category']['associations']['categories']['category']:
        available_sub_sub_categories.add(available_sub_sub_category['id'])
    
    # SUB SUB CATEGORY
     # get all sub sub categories 
    sub_sub_category= prestashop.get("categories", options={
        "filter[name]": product.get("Sub_sub_category")
    })
    sub_sub_category_id = 0
    
    
    # check which sub category is sub category for our main category
    for single_sub_sub_category in sub_sub_category['categories']['category']:
        if isinstance(sub_sub_category['categories']['category'], list): 
            if single_sub_sub_category['attrs']['id'] in available_sub_sub_categories:
                sub_sub_category_id = single_sub_sub_category['attrs']['id']
        else:
            sub_sub_category_id = sub_sub_category['categories']['category']["attrs"]["id"]
      
    return (main_category_id, sub_category_id, sub_sub_category_id)

def add_features(attributes: dict) -> dict:
    feat_ids_values = dict()
    for name, value in attributes.items():
        name = re.sub(r"\[.*?\]|<|>", "", name)
        value = re.sub(r"\[.*?\]|<|>|=", "", value)
        if len(value) > 255:
            continue
        feature = prestashop.get("product_features", options={
            "filter[name]": name
        })
        if feature["product_features"]:
            feature_id = feature["product_features"]["product_feature"]["attrs"]["id"]
        else:
            feature_schema["product_feature"]["name"]["language"]["value"] = name
            feature_schema["product_feature"]["position"] = 1
            feature_id = prestashop.add(
                "product_features", feature_schema)["prestashop"]["product_feature"]["id"]

        feature_option_schema["product_feature_value"]["id_feature"] = feature_id
        feature_option_schema["product_feature_value"]["value"]["language"]["value"] = value
        feature_option_schema["product_feature_value"]["custom"] = 1
        value_id = prestashop.add(
            "product_feature_values", feature_option_schema)["prestashop"]["product_feature_value"]["id"]
        feat_ids_values[feature_id] = value_id
    return feat_ids_values

def add_product(product: dict) -> None:
    feature_ids = add_features(product["attributes"])
    main_category_id, sub_category_id, sub_sub_category_id = get_product_categories(product)
        
    product_schema["product"]["name"]["language"]["value"] = product["Name"]
    product_schema["product"]["id_category_default"] = sub_sub_category_id
    product_schema["product"]["id_shop_default"] = 1
    product_schema["product"]["id_tax_rules_group"] = 1
    product_schema["product"]["price"] = product["Price"]
    product_schema["product"]["active"] = 1
    product_schema["product"]["state"] = 1
    product_schema["product"]["available_for_order"] = 1
    product_schema["product"]["minimal_quantity"] = 1
    product_schema["product"]["show_price"] = 1
    product_schema["product"]["link_rewrite"]["language"]["value"] = re.sub(
        r"[^a-zA-Z0-9]+", "-", product["Name"]).lower()
    product_schema["product"]["meta_title"]["language"]["value"] = product["Name"]
    
    product_features = []
    for feature_id, value_id in feature_ids.items():
        product_features.append({
            "id": feature_id,
            "id_feature_value": value_id
        })
    product_schema["product"]["associations"]["product_features"]["product_feature"] = product_features
    product_schema["product"]["associations"]["categories"] = {
        "category": [
            {"id": 2},
            {"id": main_category_id},
            {"id": sub_category_id},
            {"id": sub_sub_category_id}
        ],
    }

    product_schema["product"]["weight"] = round(product["Weight"],2)
    product_schema["product"]["description_short"]["language"][
        "value"] = product['Name']
    product_schema["product"]["description"]["language"][
        "value"] = f"{product['Name']}<br><br>Masa produktu: {round(product['Weight'], 2)} kg."
    product_id = prestashop.add("products", product_schema)[
        "prestashop"]["product"]["id"]
    
    schema_id = prestashop.search("stock_availables", options={"filter[id_product]": product_id})[0]
    stock_available_schema = prestashop.get("stock_availables", resource_id=schema_id)
    stock_available_schema["stock_available"]["quantity"] = random.randint(0, 10)
    stock_available_schema["stock_available"]["depends_on_stock"] = 0
    prestashop.edit("stock_availables", stock_available_schema)
    
    try:
        fd = io.open(f"{SCRIPT_DIR}ScrapResults/img/{product['Image']}", "rb")
        content = fd.read()
        fd.close()
        
        prestashop.add(f"images/products/{product_id}", files=[
            ('image', product["Image"], content)
        ])
    except:
        print("error")
    
def add_products(restart: bool = False) -> None:
    if restart:
        products = prestashop.get("products")["products"]
        if products:
            products_data = products["product"]

            if isinstance(products_data, dict):
                products_data = [products_data]

            ids = [int(product["attrs"]["id"]) for product in products_data]
            if ids:
                print("Deleting products...")
                prestashop.delete("products", resource_ids=ids)

        features = prestashop.get("product_features")["product_features"]
        if features:
            features_data = prestashop.get("product_features")[
                "product_features"]["product_feature"]

            if isinstance(features_data, dict):
                features_data = [features_data]

            ids = [int(feature["attrs"]["id"]) for feature in features_data]
            if ids:
                print("Deleting features...")
                prestashop.delete("product_features", resource_ids=ids)

    with open(f"{SCRIPT_DIR}ScrapResults/json/data.json") as file:
        products = json.loads(file.read())
    for product in products:
        add_product(product)
     
def add_categories(restart: bool = False) -> None:
    if restart:
        ids = []
        for category in prestashop.get("categories")["categories"]["category"]:
            if int(category["attrs"]["id"]) not in [1, 2]:
                ids.append(int(category["attrs"]["id"]))
        if ids:
            print("Deleting categories...")
            prestashop.delete("categories", resource_ids=ids)

        with open(f"{SCRIPT_DIR}ScrapResults/json/category.json") as file:
            categories = json.loads(file.read())
            
        for main_category, sub_category_value in categories.items():
            main_category_id = add_category(main_category, 2)
            if isinstance(sub_category_value, dict):
                for sub_category, sub_sub_category_value in sub_category_value.items():
                    sub_category_id = add_category(sub_category, main_category_id)
                    if isinstance(sub_sub_category_value, (list, dict)):
                        for sub_sub_category in sub_sub_category_value:
                            sub_sub_category_id = add_category(sub_sub_category, sub_category_id)
    else:
        return

if __name__ == "__main__":
    prestashop = prestapyt.PrestaShopWebServiceDict(LINK, API_KEY)
    
    category_schema = prestashop.get("categories", options={
        "schema": "blank"
    })
    product_schema = prestashop.get("products", options={
        "schema": "blank"
    })

    del product_schema["product"]["position_in_category"]
    del product_schema["product"]["associations"]["combinations"]
    
    feature_schema = prestashop.get("product_features", options={
        "schema": "blank"
    })

    feature_option_schema = prestashop.get("product_feature_values", options={
        "schema": "blank"
    })
    
    add_categories(restart=True)
    add_products(restart=True)