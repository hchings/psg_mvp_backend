"""
A simple hard-coded script to load users from csv.
Customize it before using.

To run:
    python manage.py runscript load_users

"""
import pandas as pd
import urllib.request
from urllib.request import Request

from users.models import User
from users.clinics.models import ClinicProfile


def run():
    # read in csv
    df = pd.read_csv("../clinics.csv", header=0)
    # clear up column name
    df.columns = [item.strip() for item in df.columns]

    print(df.head())

    for col, row in df.iterrows():
        name = row['clinic name'].strip().split("(")[0].split("（")[0]
        website = str(row['website']).strip()
        fb_url = str(row['fb_url']).split(",")[0]
        print(name, website)
        print("fb:", fb_url)

        # create user
        clinic = User(username=name, password='123456', user_type='clinic')

        try:
            # ans = input("go?")
            # if ans == 'y':
            clinic.save()
            #     print("saved")
            # else:
            #     print("skip saving")
        except:
            # duplicated username
            print("SKIPPED")

        # get profile
        profile = ClinicProfile.objects.get(display_name=clinic.username)
        print(profile)

        try:
            req = Request(website,
                          headers={'User-Agent': 'Mozilla/5.0'})
            code = urllib.request.urlopen(req).getcode()
            print("web: ", code)
            if int(code) == 200:
                profile.website_url = website
        except Exception as e:
            print(e)

        try:
            # need headers otherwise might get 403
            req = Request(fb_url,
                          headers={'User-Agent': 'Mozilla/5.0'})
            fb_code = urllib.request.urlopen(req).getcode()
            print("fb: ", fb_code)
            if int(fb_code) == 200:
                profile.fb_url = fb_url
        except Exception as e:
            print(e)

        profile.save()
