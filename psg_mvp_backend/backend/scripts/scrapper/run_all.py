"""
Script to run node scrape_review on clinic one by one.

"""
import os
import json

if __name__ == '__main__':
    with open('urls.full.json') as f:
        data = json.load(f)

    for clinic in data["results"]:
        print(clinic)
        if clinic["source"] == "facebook":
            print("we have facebook")
        if clinic["source"] == "google":
            print("we have google")

            clinic_uuid = clinic["clinic_uuid"] or "missing"
            branch = clinic["branch"] or "missing"
            place_id = clinic["placeId"] or "missing"
            url = clinic["url"] or "missing"

            os.system('cd gl_map_review; node scrape.js %s %s %s "%s"' % (clinic_uuid, branch, place_id, url))

        # if i >= 100:
        #     break

    print("there was an attempt TG!")
