#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from pprint import pprint

from api import AkeneoAPI

akeneo = AkeneoAPI(
    url="AKENEO_INSTANCE_URL",
    client_id="YOUR_CLIENT_ID",
    secret="YOUR_SECRET",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
    verbose=False
)

# GET Attributes
atributes = akeneo.get('attributes')
akeneo.log.info(pprint(atributes))

# GET Channels
channels = akeneo.get('channels')
akeneo.log.info(pprint(channels))
channel = akeneo.get('channels', id='ecommerce')
akeneo.log.info(pprint(channel))

# Filters (GET with filters) products
dt = datetime.strptime('2016-08-22 14:00:00', '%Y-%m-%d %H:%M:%S')
products = akeneo.filter('products', search_by='updated', search_operator='>', search_value=dt)
akeneo.log.info(pprint(products))

# POST a product
data = {"identifier":"top1","enabled":True,"categories":[],"groups":[],"variant_group":None,"values":{"name":[{"data":"Débardeur","locale":None,"scope":None}],"description":[{"data":"Summer top","locale":"en_US","scope":"ecommerce"},{"data":"Débardeur pour l'été","locale":"fr_FR","scope":"ecommerce"}],"price":[{"locale":None,"scope":None,"data":[{"amount":"155","currency":"EUR"},{"amount":"15","currency":"USD"}]}]}}  # noqa
new_product = akeneo.post('products', data)
akeneo.log.info(pprint(new_product))

# PATCH a product
update_data = [{"identifier": "top", "enabled": True}, {"identifier": "top1", "enabled": True}]
update_product = akeneo.patch('products', update_data)
akeneo.log.info(pprint(update_product))

del_product = akeneo.delete('products', 'top1')
akeneo.log.info(pprint(del_product))

# POST a media-file
file = open('fff_600x400.png', 'rb')
product_obj = {"identifier": "toto", "attribute": "picture", "scope": None, "locale": None}
new_media_file = akeneo.post('media-files', data=product_obj, file=file)
akeneo.log.info(pprint(new_media_file))

file_id = 'd/7/4/5/d745c18d2739e09c1c4996c64bce9755386e8c86_fff_600x400.png'
get_media_file = akeneo.get('media-files', id=file_id)
akeneo.log.info(pprint(get_media_file))

akeneo.close_session()
