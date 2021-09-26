"""
Script to run node scrape_review on clinic one by one.

"""
import os
import json

if __name__ == '__main__':
    with open('urls.full.json') as f:
        data = json.load(f)

    for idx, clinic in enumerate(data["results"]):
        # if idx == 0:
        #     continue
        # if idx > 2 :
        #    break
        clinic_uuid = clinic["clinic_uuid"] or "missing"
        branch = clinic["branch"] or "missing"
        place_id = clinic["placeId"] or "missing"
        url = clinic["url"] or "missing"

        if clinic["source"] == "facebook":
            print('facebook clinic idx=%s; node index.js --url "%s" --uuid "%s"' % (idx, url, clinic_uuid))
            os.system('cd puppeteer-login-for-facebook; node index.js --url "%s" --uuid "%s"' % (url, clinic_uuid))
        if clinic["source"] == "google":
            continue
            print('google clinic idx=%s; node scrape.js %s %s %s "%s"' % (clinic_uuid, branch, place_id, url))
            os.system('cd gl_map_review; node scrape.js %s %s %s "%s"' % (clinic_uuid, branch, place_id, url))

        # if i >= 100:
        #     break

    print("there was an attempt TG!")

