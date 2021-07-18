"""
Script to run node scrape_review on clinic one by one.

"""
import os
import json

if __name__ == '__main__':
    with open('urls.full.json') as f:
        data = json.load(f)

    for idx, clinic in enumerate(data["results"]):
        # if idx > 1:
        #     break
        # print(clinic)
        clinic_uuid = clinic["clinic_uuid"] or "missing"
        branch = clinic["branch"] or "missing"
        place_id = clinic["placeId"] or "missing"
        url = clinic["url"] or "missing"

        if clinic["source"] == "facebook":
            print("we have facebook")
            #{"source": "facebook", "clinic_uuid": "915799337850471", "branch": "", "placeId": "", "url": "https://www.facebook.com/Dr.LaMer.Clinic/reviews/?ref=page_internal"}
            os.system('cd fb_map_review; python fb_scrapper.py %s "%s"' % (clinic_uuid, url))
        if clinic["source"] == "google":
            continue
            print("we have google")
            os.system('cd gl_map_review; node scrape.js %s %s %s "%s"' % (clinic_uuid, branch, place_id, url))

        # if i >= 100:
        #     break

    print("there was an attempt TG!")

