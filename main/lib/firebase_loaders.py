from main.models import Restaurant, Cuisine, Highlight, Dish, Keyword, Blog, Profile, Like
import datetime
from django.utils.text import slugify
from django.contrib.auth.models import User


def int_to_time(seconds):
    hours = abs(int(seconds / 3600)) % 24
    mins = abs(int((seconds % 3600) / 60))
    sec = abs(int((seconds % 3600) % 60))
    return datetime.time(hours, mins, sec)


def save_restaurant(item, key):
    point = 'POINT({} {})'.format(item['location'][1], item['location'][0])
    params = {
        'firebase_id': key, 'address': item['address'],
        'suburb': item['suburb'], 'name': item['name'],
        'image_url': item['imageURL'], 'information': item['information'],
        'tripadvisor_widget': item['tripAdvisorWidget'],
        'location': point, 'phone_number': item['phoneNumber'],
        'time_offset_minutes': item['timeOffsetFromUTC']*60,
        'quandoo_id': item.get('quandoo_id', None)
    }
    restaurant, created = Restaurant.objects.update_or_create(**params)
    return restaurant


def save_dish(item, key):
    restaurant = Restaurant.objects.get(firebase_id=item['_restaurant'])
    params = {
        'firebase_id': key, 'restaurant': restaurant, 'title': item['title'],
        'price': int(item['price']*100), 'image_url': item['imageURL'],
        'instagram_user': item.get('instagramUser', '')
    }
    dish, created = Dish.objects.update_or_create(**params)
    return dish


def save_blog(item, key):
    params = {
        'firebase_id': key, 'author': item.get('author', ''),
        'image_url': item.get('imageURL', ''), 'title': item.get('title', ''),
        'url': item.get('url', '')
    }
    blog, created = Blog.objects.update_or_create(**params)
    return blog


def save_user(item, key):
    try:
        user = User.objects.get(profile__firebase_id=key)
    except User.DoesNotExist:
        try:
            pdata = item['providerData'][0]
        except KeyError:
            return False
        params = {
            'email': pdata.get('email', '')[:254],
            'username': pdata.get('uid', pdata.get('email', ''))[:150],
            'first_name': item.get('firstname', '')[:30],
            'last_name': item.get('lastname', '')[:30],
        }
        user = User(**params)
        user.save()
        save_profile(pdata, key, user).save()
    return user


def save_profile(pdata, key, user):
    profile = Profile(provider=pdata['providerID'], firebase_id=key, user=user)
    if pdata['providerID'] == 'facebook.com':
        profile.fb_id = pdata['uid']
        profile.photo_url = pdata.get('photoURL', '')
    return profile


def save_like(item, key):
    for junk_key, dish_item in item.items():
        print(dish_item, junk_key)
        try:
            dish = Dish.objects.get(firebase_id=dish_item['_dish'])
            user = User.objects.get(profile__firebase_id=dish_item['_user'])
            like = Like(dish=dish, user=user, did_like=dish_item['didLike'])
        except Dish.DoesNotExist:
            print('Does not exist:', dish_item['_dish'], dish_item['_user'])


def save_manytomany(parent, list, mtm_class_name, prop_name):
    mtm_class = globals()[mtm_class_name]
    mtm_name = mtm_class_name.lower()+'s'
    params = {}
    defaults = {}
    for new_item in list:
        if len(new_item) > 1:
            params[prop_name] = new_item
            if hasattr(mtm_class, 'slug'):
                params['slug'] = slugify(new_item)
                del params[prop_name]
                defaults[prop_name] = new_item
            obj, created = mtm_class.objects.get_or_create(defaults=defaults, **params)
            getattr(parent, mtm_name).add(obj)
