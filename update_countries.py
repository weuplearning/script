#!/usr/bin/env python

import os
import importlib
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#Script for handling encoding error in country field for user profile/custom_field


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms.envs.aws")
os.environ.setdefault("lms.envs.aws,SERVICE_VARIANT", "lms")
os.environ.setdefault("PATH", "/edx/app/edxapp/venvs/edxapp/bin:/edx/app/edxapp/edx-platform/bin:/edx/app/edxapp/.rbenv/bin:/edx/app/edxapp/.rbenv/shims:/edx/app/edxapp/.gem/bin:/edx/app/edxapp/edx-platform/node_modules/.bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin")

os.environ.setdefault("SERVICE_VARIANT", "lms")
os.chdir("/edx/app/edxapp/edx-platform")

startup = importlib.import_module("lms.startup")
startup.run()

from django.core.management import execute_from_command_line
import django

#Script imports
#A lot of useless import -
import argparse, sys
from opaque_keys.edx.keys import CourseKey
from courseware.courses import get_course_by_id
from microsite_configuration.models import Microsite
from courseware.courses import get_courses
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.course_groups.cohorts import get_cohort_names
from tma_stat_dashboard.grade_reports import grade_reports
from student.models import CourseEnrollment, UserProfile
from tma_apps.models import TmaCourseEnrollment

import json
from datetime import datetime
from django.utils.timezone import UTC
import logging
log = logging.getLogger()


#associated_countries is a correlation table of possible values extract from the users already registered
associated_countries = [
 {"FR":"FR"},
 {"BE":"BE"},
 {"ES":"ES"},
 {"France":"FR"},
 {"Espa\\u00f1a":"ES"},
 {"Italie":"IT"},
 {"Espana":"ES"},
 {"Espagne":"ES"},
 {"Nederland":"NL"},
 {"Netherlands":"NL"},
 {"Belgium":"BE"},
 {"Pays-Bas":"NL"},
 {"United States of America":"US"},
 {"United Kingdom":"UK"},
 {"Singapore":"SG"},
 {"Russia":"RU"},
 {"Argentine":"AR"},
 {"Afrique du Sud":"ZA"},
 {"Albanie":"AL"},
 {"Afghanistan":"AF"},
 {"Canada":"CA"},
 {"Belgi\\u00eb":"BE"},
 {"Portugal":"PT"},
 {"Belgique":"BE"},
 {"\\u4e2d\\u56fd":"CN"},
 {"Chine":"CN"},
 {"Andorre":"AD"},
 {"United States Minor Outlying Islands":"UM"},
 {"Nigeria":"NG"},
 {"Australia":"AU"},
 {"South Africa":"ZA"},
 {"Sweden":"SE"},
 {"Lithuania":"LT"},
 {"India":"IN"},
 {"Argentina":"AR"},
 {"Zimbabwe":"ZW"},
 {"Bahre\\u00efn":"BH"},
 {"Spain":"ES"},
 {"Norway":"NO"},
 {"Macedonia":"MK"},
 {"Ukraine":"UA"},
 {"Bahamas":"BS"},
 {"Brazil":"BR"},
 {"Switzerland":"CH"},
 {"Italy":"IT"},
 {"Allemagne":"DE"},
 {"Venezuela":"VE"},
 {"Germany":"DE"},
 {"China":"CN"},
 {"\\u53f0\\u6e7e":"TW"},
 {"Hong Kong":"HK"},
 {"Luxembourg":"LU"},
 {"Japan":"JP"},
 {"Japon":"JP"},
 {"Turkey":"TR"},
 {"Peru":"PE"},
 {"Poland":"PL"},
 {"Dominican Republic":"DO"},
 {"Ecuador":"EC"},
 {"Mexico":"MX"},
 {"Costa Rica":"CR"},
 {"New Zealand":"NZ"},
 {"Bulgaria":"BG"},
 {"Isle of Man":"IM"},
 {"Jersey":"JE"},
 {"\\u65e5\\u672c":"JP"},
 {"\u65e5\u672c":"JP"},
 {"Denmark":"DK"},
 {"Taiwan":"TW"},
 {"Malaysia":"MY"},
 {"Thailand":"TH"},
 {"Suisse":"CH"},
 {"Bulgarie":"BG"},
 {"Moldavie":"MD"},
 {"Vietnam":"VN"},
 {"Czech Republic":"CZ"},
 {"Austria":"AT"},
 {"Roumanie":"RO"},
 {"Albania":"AL"},
 {"\\u53f0\\u7063":"TW"},
 {"Mauritius":"MU"},
 {"Belarus":"BY"},
 {"Armenia":"AM"},
 {"\\u0423\\u043a\\u0440\\u0430\\u0438\\u043d\\u0430":"UA"},
 {"Moldova":"MD"},
 {"\\u0420\\u043e\\u0441\\u0441\\u0438\\u044f":"RU"},
 {"Russie":"RU"},
 {"Arm\\u00e9nie":"AM"},
 {"Deutschland":"DE"},
 {"Finland":"FR"},
 {"Taiwain, SAR":"TW"},
 {"Lebanon":"LB"},
 {"Ireland":"IE"},
 {"Su\\u00e8de":"SE"},
 {"Slovenia":"SI"},
 {"Greece":"GR"},
 {"South Korea":"KR"},
 {"Royaume-Uni":"UK"},
 {"Puerto Rico":"PR"},
 {"Hong-Kong , SAR":"HK"},
 {"Autriche":"AT"},
 {"Australie":"AU"},
 {"\\u82f1\\u56fd":"UK"},
 {"Romania":"RO"},
 {"Chile":"CL"},
 {"Latvia":"LT"},
 {"Hungary":"HU"},
 {"Philippines":"PH"},
 {"Palestine, State of":"PS"},
 {"United Arab Emirates":"AR"},
 {"Taiwan, SAR":"TW"},
 {"Etats Unis d'Am\\u00e9rique":"US"},
 {"Guernsey":"GG"},
 {"Colombia":"CO"},
 {"Aruba":"AW"},
 {"Hong-Kong, SAR":"HK"},
 {"Norv\\u00e8ge":"NO"},
 {"Finlande":"FI"},
 {"R\\u00e9publique tch\\u00e8que":"CZ"},
 {"Cameroon":"CM"},
 {"\\u53f0\\u7063\\u5730\\u5340":"TW"},
 {"Taiwan region":"TW"},
 {"Bangladesh":"BD"},
 {"Mexique":"MX"},
 {"Polyn\\u00e9sie fran\\u00e7aise":"PF"},
 {"Hongrie":"HU"},
 {"\\u0411\\u0435\\u043b\\u0430\\u0440\\u0443\\u0441\\u044c":"BY"},
 {"Slovakia":"SK"},
 {"\\u00c5land Islands":"AX"},
 {"S\\u00e9n\\u00e9gal":"SN"},
 {"Indonesia":"ID"},
 {"Iceland":"IS"},
 {"Bahrain":"BH"},
 {"Djibouti":"DJ"},
 {"AT":"AT"},
 {"AQ":"AQ"},
 {"IT":"IT"},
 {"US":"US"},
 {"JP":"JP"},
 {"CA":"CA"},
 {"RU":"RU"},
 {"TW":"TW"},
 {"CH":"CH"},
 {"GB":"GB"},
]


# Getting the enrolled user for a course, the course is as args
course_key=CourseKey.from_string(sys.argv[1])
course=get_course_by_id(course_key)
course_enrollments=CourseEnrollment.objects.filter(course_id=course_key, is_active=1)
userNotUpdated = []
countryNotUpdated = []

# Looping through the user list
for enrollment in course_enrollments :
    user= enrollment.user
    # Getting the custom field precisely the country field and getting also the country field from the user profil
    # Getting the user profil
    userJson = UserProfile.objects.get(user=user)
    # Getting the custom field from it
    custom_field = json.loads(userJson.custom_field)
    #Getting the field country from the custom field
    countryUserCustom=custom_field.get('country')

    addingToList = False;
    log.info("-------------------------- treating user {} for grade report -------------------------".format(user.email))

    #Looping through the correlation table
    for country in associated_countries:
        #If there is a correlation between the country in the custom_field, the field country of profil is updated
        if str(countryUserCustom) == str(next(iter(country))):
            addingToList = True
            custom_field['country'] = country[str(next(iter(country)))]
            userJson.country = country[str(next(iter(country)))]
            userJson.custom_field = json.dumps(custom_field)
            break
            #userJson.save()
        else:
            if str(countryUserCustom)[:2] == 'Su':
                addingToList = True
                custom_field['country'] = 'SE'
                userJson.country = 'SE'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******Sweden******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom)[:4] == 'Espa':
                addingToList = True
                custom_field['country'] = 'ES'
                userJson.country = 'ES'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******Spain******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom)[:5] == 'Belgi':
                addingToList = True
                custom_field['country'] = 'BE'
                userJson.country = 'BE'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******Belgium******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom)[:3] == 'Arm':
                addingToList = True
                custom_field['country'] = 'AM'
                userJson.country = 'AM'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******Armenia******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom)[:5] == 'Polyn':
                addingToList = True
                custom_field['country'] = 'PF'
                userJson.country = 'PF'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******French Polynesia******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom)[:10] == 'Etats Unis':
                addingToList = True
                custom_field['country'] = 'US'
                userJson.country = 'US'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******United state of america******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom)[:4] == 'Norv':
                addingToList = True
                custom_field['country'] = 'NO'
                userJson.country = 'NO'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******Norway******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom)[:5] == 'Bahre':
                addingToList = True
                custom_field['country'] = 'BH'
                userJson.country = 'BH'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******Bahrein******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom)[:1] == 'S' and str(countryUserCustom)[-3:] == 'gal':
                addingToList = True
                custom_field['country'] = 'SN'
                userJson.country = 'SN'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******Senegal******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom)[:1] == 'R' and str(countryUserCustom)[-3:] == 'que':
                addingToList = True
                custom_field['country'] = 'CZ'
                userJson.country = 'CE'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******Czechia******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom)[-12:] == 'land Islands':
                addingToList = True
                custom_field['country'] = 'AX'
                userJson.country = 'AX'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******Aland island******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom) == 'None':
                addingToList = True
                custom_field['country'] = 'FR'
                userJson.country = 'FR'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******None******-------------------------------------------------------------------------------------')
                break
            elif str(countryUserCustom) == '0':
                addingToList = True
                custom_field['country'] = 'FR'
                userJson.country = 'FR'
                userJson.custom_field = json.dumps(custom_field)
                log.info('-------------------------------------------------------------------------******0******-------------------------------------------------------------------------------------')
                break

            elif not addingToList:
                addingToList = False
    if not addingToList:
        log.warning("{} is not in the correlation table !".format(str(countryUserCustom)))
        log.warning("Adding user {} to the list to check".format(user.email))
        userInfo = {user.email : [countryUserCustom,userJson.country]}
        if str(countryUserCustom) not in countryNotUpdated:
            countryNotUpdated.append(str(countryUserCustom))
        userNotUpdated.append(userInfo)
    else :
        log.info("{} is in the correlation table !".format(str(countryUserCustom)))
        log.info("Updating country field with the correct value")
        log.info("User {} is updated".format(user.email))

log.warning('--------------------------------------------------- Warning the following user(s) has not been updated ! ---------------------------------------------------')
log.warning('------------------------------------------------------------------ {} users ------------------------------------------------------------------'.format(len(userNotUpdated)))
log.warning(userNotUpdated)
log.warning('------------------------------------------------------------------ Countries not updated ------------------------------------------------------------------')
log.warning(countryNotUpdated)
