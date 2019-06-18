from flask import Flask, request, render_template, make_response
import webbrowser
import sys
import os
import io
from lxml import etree
from csv import writer as csvwriter
import codecs


def activity_data(activity):
    activity_level_data = []
    try:
        id = activity.xpath("iati-identifier")[0].text
    except (IndexError, KeyError):
        id = ""
    activity_level_data.append(id)

    try:
        default_currency = activity.attrib['default-currency']
    except (IndexError, KeyError):
        default_currency = "GBP"
    activity_level_data.append(default_currency)

    default_lang = "en"
    activity_level_data.append(default_lang)

    try:
        humanitarian = activity.attrib['humanitarian']
    except (IndexError, KeyError):
        humanitarian = ""
    activity_level_data.append(humanitarian)

    try:
        title = activity.xpath("title/narrative")[0].text
    except (IndexError, KeyError):
        title = ""
    activity_level_data.append(title)

    descriptions = activity.xpath("description")
    general_description = ""
    objective_description = ""
    target_description = ""
    other_description = ""
    for description in descriptions:
        try:
            description_type = description.attrib['type']
        except (IndexError, KeyError):
            description_type = "1"
        if description_type == "1":
            try:
                general_description += description.xpath("narrative")[0].text
            except (IndexError, KeyError):
                pass
        if description_type == "2":
            try:
                objective_description += description.xpath("narrative")[0].text
            except (IndexError, KeyError):
                pass
        if description_type == "3":
            try:
                target_description += description.xpath("narrative")[0].text
            except (IndexError, KeyError):
                pass
        if description_type == "4":
            try:
                other_description += description.xpath("narrative")[0].text
            except (IndexError, KeyError):
                pass
    activity_level_data.append(general_description)
    activity_level_data.append(objective_description)
    activity_level_data.append(target_description)
    activity_level_data.append(other_description)

    try:
        status = activity.xpath("activity-status")[0].attrib['code']
    except (IndexError, KeyError):
        status = ""
    activity_level_data.append(status)

    activity_dates = activity.xpath("activity-date")
    actual_start = ""
    actual_end = ""
    planned_start = ""
    planned_end = ""
    for activity_date in activity_dates:
        try:
            date_type = activity_date.attrib['type']
        except (IndexError, KeyError):
            date_type = "1"
        if date_type == "1":
            try:
                planned_start = activity_date.attrib['iso-date']
            except (IndexError, KeyError):
                pass
        if date_type == "2":
            try:
                actual_start = activity_date.attrib['iso-date']
            except (IndexError, KeyError):
                pass
        if date_type == "3":
            try:
                planned_end = activity_date.attrib['iso-date']
            except (IndexError, KeyError):
                pass
        if date_type == "4":
            try:
                actual_end = activity_date.attrib['iso-date']
            except (IndexError, KeyError):
                pass
    activity_level_data.append(actual_start)
    activity_level_data.append(actual_end)
    activity_level_data.append(planned_start)
    activity_level_data.append(planned_end)

    participating_orgs = activity.xpath("participating-org")
    participating_org_roles = []
    participating_org_types = []
    participating_org_names = []
    participating_org_refs = []
    for org in participating_orgs:
        try:
            org_role = str(org.attrib['role'])
        except (IndexError, KeyError):
            org_role = ""
        participating_org_roles.append(org_role)
        try:
            org_type = str(org.attrib['type'])
        except (IndexError, KeyError):
            org_type = ""
        participating_org_types.append(org_type)
        try:
            org_name = str(org.xpath("narrative")[0].text)
        except (IndexError, KeyError):
            org_name = ""
        participating_org_names.append(org_name)
        try:
            org_ref = str(org.attrib['ref'])
        except (IndexError, KeyError):
            org_ref = ""
        participating_org_refs.append(org_ref)
    participating_org_role = ";".join(participating_org_roles)
    participating_org_type = ";".join(participating_org_types)
    participating_org_name = ";".join(participating_org_names)
    participating_org_ref = ";".join(participating_org_refs)
    activity_level_data.append(participating_org_role)
    activity_level_data.append(participating_org_type)
    activity_level_data.append(participating_org_name)
    activity_level_data.append(participating_org_ref)

    activity_recip_countries = activity.xpath("recipient-country")
    activity_recip_codes = []
    activity_recip_percentages = []
    for act_recip_country in activity_recip_countries:
        try:
            act_recip_code = str(act_recip_country.attrib['code'])
        except (IndexError, KeyError):
            act_recip_code = ""
        activity_recip_codes.append(act_recip_code)
        try:
            act_recip_perc = str(act_recip_country.attrib['percentage'])
        except (IndexError, KeyError):
            act_recip_perc = ""
        activity_recip_percentages.append(act_recip_perc)
    activity_recip_code = ";".join(activity_recip_codes)
    activity_recip_percentage = ";".join(activity_recip_percentages)
    activity_level_data.append(activity_recip_code)
    activity_level_data.append(activity_recip_percentage)

    activity_recip_regions = activity.xpath("recipient-region")
    activity_recip_region_codes = []
    activity_recip_region_percentages = []
    for act_recip_region in activity_recip_regions:
        try:
            act_recip_region_code = str(act_recip_region.attrib['code'])
        except (IndexError, KeyError):
            act_recip_region_code = ""
        activity_recip_region_codes.append(act_recip_region_code)
        try:
            act_recip_region_perc = str(act_recip_region.attrib['percentage'])
        except (IndexError, KeyError):
            act_recip_region_perc = ""
        activity_recip_region_percentages.append(act_recip_region_perc)
    activity_recip_region_code = ";".join(activity_recip_region_codes)
    activity_recip_region_percentage = ";".join(activity_recip_region_percentages)
    activity_level_data.append(activity_recip_region_code)
    activity_level_data.append(activity_recip_region_percentage)

    activity_sectors = activity.xpath("sector")
    activity_sector_vocabs = []
    activity_sector_codes = []
    activity_sector_percs = []
    for activity_sector in activity_sectors:
        try:
            act_sector_vocab = str(activity_sector.attrib['vocabulary'])
        except (IndexError, KeyError):
            act_sector_vocab = ""
        activity_sector_vocabs.append(act_sector_vocab)
        try:
            act_sector_code = str(activity_sector.attrib['code'])
        except (IndexError, KeyError):
            act_sector_code = ""
        activity_sector_codes.append(act_sector_code)
        try:
            act_sector_perc = str(activity_sector.attrib['percentage'])
        except (IndexError, KeyError):
            act_sector_perc = ""
        activity_sector_percs.append(act_sector_perc)
    activity_sector_vocab = ";".join(activity_sector_vocabs)
    activity_sector_code = ";".join(activity_sector_codes)
    activity_sector_percs = ";".join(activity_sector_percs)
    activity_level_data.append(activity_sector_vocab)
    activity_level_data.append(activity_sector_code)
    activity_level_data.append(activity_sector_percs)
    return activity_level_data


# Initialize app, checking if frozen in exe
if getattr(sys, 'frozen', False):
    template_folder = os.path.abspath(os.path.join(sys.executable, '..', 'templates'))
    static_folder = os.path.abspath(os.path.join(sys.executable, '..', 'static'))
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)


# Set "homepage" to index.html
@app.route('/')
def index():
    return render_template('index.html', message="Drag a file to be converted onto this page.")


# Route to convert transactions
@app.route('/convert_transactions', methods=["POST"])
def convert_transactions():
    fileob = request.files["xmlfile"]
    original_basename, _ = os.path.splitext(fileob.filename)
    tree = etree.parse(fileob)
    root = tree.getroot()

    mem_buffer = io.BytesIO()
    codecinfo = codecs.lookup("utf8")
    buffer_wrapper = codecs.StreamReaderWriter(mem_buffer, codecinfo.streamreader, codecinfo.streamwriter)
    cw = csvwriter(buffer_wrapper)
    col_names = [
        "Activity Identifier",
        "Activity Default Currency",
        "Activity Default Language",
        "Humanitarian",
        "Activity Title",
        "Activity Description (General)",
        "Activity Description (Objectives)",
        "Activity Description (Target Groups)",
        "Activity Description (Others)",
        "Activity Status",
        "Actual Start Date",
        "Actual End Date",
        "Planned Start Date",
        "Planned End Date",
        "Participating Organisation Role",
        "Participating Organisation Type",
        "Participating Organisation Name",
        "Participating Organisation Identifier",
        "Recipient Country Code",
        "Recipient Country Percentage",
        "Recipient Region Code",
        "Recipient Region Percentage",
        "Sector Vocabulary",
        "Sector Code",
        "Sector Percentage",
        "Transaction Internal Reference",
        "Transaction Type",
        "Transaction Date",
        "Transaction Value",
        "Transaction Value Date",
        "Transaction Description",
        "Transaction Provider Organisation Identifier",
        "Transaction Provider Organisation Type",
        "Transaction Provider Organisation Activity Identifier",
        "Transaction Provider Organisation Description",
        "Transaction Receiver Organisation Identifier",
        "Transaction Receiver Organisation Type",
        "Transaction Receiver Organisation Activity Identifier",
        "Transaction Receiver Organisation Description",
        "Transaction Sector Vocabulary",
        "Transaction Sector Code",
        "Transaction Recipient Country Code",
        "Transaction Recipient Region Code",
    ]
    cw.writerow(col_names)

    for activity in root.getchildren():
        activity_level_data = activity_data(activity)

        transactions = activity.xpath("transaction")
        for transaction in transactions:
            transaction_level_data = []

            try:
                trans_id = transaction.attrib['ref']
            except (IndexError, KeyError):
                trans_id = ""
            transaction_level_data.append(trans_id)

            try:
                trans_type = transaction.xpath("transaction-type")[0].attrib['code']
            except (IndexError, KeyError):
                trans_type = ""
            transaction_level_data.append(trans_type)

            try:
                trans_date = transaction.xpath("transaction-date")[0].attrib["iso-date"]
            except (IndexError, KeyError):
                trans_date = ""
            transaction_level_data.append(trans_date)

            try:
                trans_value = transaction.xpath("value")[0].text
            except (IndexError, KeyError):
                trans_value = ""
            transaction_level_data.append(trans_value)

            try:
                trans_value_date = transaction.xpath("value")[0].attrib["value-date"]
            except (IndexError, KeyError):
                trans_value_date = ""
            transaction_level_data.append(trans_value_date)

            try:
                trans_description = transaction.xpath("description/narrative")[0].text
            except (IndexError, KeyError):
                trans_description = ""
            transaction_level_data.append(trans_description)

            try:
                trans_provider_org_id = transaction.xpath("provider-org")[0].attrib['ref']
            except (IndexError, KeyError):
                trans_provider_org_id = ""
            transaction_level_data.append(trans_provider_org_id)

            try:
                trans_provider_org_type = transaction.xpath("provider-org")[0].attrib['type']
            except (IndexError, KeyError):
                trans_provider_org_type = ""
            transaction_level_data.append(trans_provider_org_type)

            try:
                trans_provider_org_activity_id = transaction.xpath("provider-org")[0].attrib['provider-activity-id']
            except (IndexError, KeyError):
                trans_provider_org_activity_id = ""
            transaction_level_data.append(trans_provider_org_activity_id)

            try:
                trans_provider_org_description = transaction.xpath("provider-org/narrative")[0].text
            except (IndexError, KeyError):
                trans_provider_org_description = ""
            transaction_level_data.append(trans_provider_org_description)

            try:
                trans_receiver_org_id = transaction.xpath("receiver-org")[0].attrib['ref']
            except (IndexError, KeyError):
                trans_receiver_org_id = ""
            transaction_level_data.append(trans_receiver_org_id)

            try:
                trans_receiver_org_type = transaction.xpath("receiver-org")[0].attrib['type']
            except (IndexError, KeyError):
                trans_receiver_org_type = ""
            transaction_level_data.append(trans_receiver_org_type)

            try:
                trans_receiver_org_activity_id = transaction.xpath("receiver-org")[0].attrib['receiver-activity-id']
            except (IndexError, KeyError):
                trans_receiver_org_activity_id = ""
            transaction_level_data.append(trans_receiver_org_activity_id)

            try:
                trans_receiver_org_description = transaction.xpath("receiver-org/narrative")[0].text
            except (IndexError, KeyError):
                trans_receiver_org_description = ""
            transaction_level_data.append(trans_receiver_org_description)

            transaction_sectors = transaction.xpath("sector")
            transaction_sector_vocabs = []
            transaction_sector_codes = []
            for transaction_sector in transaction_sectors:
                try:
                    trans_sector_vocab = str(transaction_sector.attrib['vocabulary'])
                except (IndexError, KeyError):
                    trans_sector_vocab = ""
                transaction_sector_vocabs.append(trans_sector_vocab)
                try:
                    trans_sector_code = str(transaction_sector.attrib['code'])
                except (IndexError, KeyError):
                    trans_sector_code = ""
                transaction_sector_codes.append(trans_sector_code)
            transaction_sector_vocab = ";".join(transaction_sector_vocabs)
            transaction_sector_code = ";".join(transaction_sector_codes)
            transaction_level_data.append(transaction_sector_vocab)
            transaction_level_data.append(transaction_sector_code)

            try:
                trans_recipient_country = transaction.xpath("recipient-country")[0].attrib['code']
            except (IndexError, KeyError):
                trans_recipient_country = ""
            transaction_level_data.append(trans_recipient_country)

            try:
                trans_recipient_region = transaction.xpath("recipient-region")[0].attrib['code']
            except (IndexError, KeyError):
                trans_recipient_region = ""
            transaction_level_data.append(trans_recipient_region)

            cw.writerow(activity_level_data + transaction_level_data)

    output = make_response(buffer_wrapper.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename={}_transactions.csv".format(original_basename)
    output.headers["Content-type"] = "text/csv"
    return output


# Route to convert transactions
@app.route('/convert_budgets', methods=["POST"])
def convert_budgets():
    fileob = request.files["xmlfile"]
    original_basename, _ = os.path.splitext(fileob.filename)
    tree = etree.parse(fileob)
    root = tree.getroot()

    mem_buffer = io.BytesIO()
    codecinfo = codecs.lookup("utf8")
    buffer_wrapper = codecs.StreamReaderWriter(mem_buffer, codecinfo.streamreader, codecinfo.streamwriter)
    cw = csvwriter(buffer_wrapper)
    col_names = [
        "Activity Identifier",
        "Activity Default Currency",
        "Activity Default Language",
        "Humanitarian",
        "Activity Title",
        "Activity Description (General)",
        "Activity Description (Objectives)",
        "Activity Description (Target Groups)",
        "Activity Description (Others)",
        "Activity Status",
        "Actual Start Date",
        "Actual End Date",
        "Planned Start Date",
        "Planned End Date",
        "Participating Organisation Role",
        "Participating Organisation Type",
        "Participating Organisation Name",
        "Participating Organisation Identifier",
        "Recipient Country Code",
        "Recipient Country Percentage",
        "Recipient Region Code",
        "Recipient Region Percentage",
        "Sector Vocabulary",
        "Sector Code",
        "Sector Percentage",
        "Policy Marker Vocabulary",  # Budget template is different from here
        "Policy Marker Code",
        "Policy Marker Significance",
        "Activity Scope",
        "Budget Type",
        "Budget Status",
        "Budget Period Start",
        "Budget Period End",
        "Budget Value",
        "Budget Value Date",
        "Budget Currency",
        "Related Activity Identifier",
        "Related Activity Type",
        "Contact Type",
        "Contact Organization",
        "Contact Department",
        "Contact Person Name",
        "Contact Job Title",
        "Contact Telephone",
        "Contact Email",
        "Contact Website",
        "Contact Mailing Address"
    ]
    cw.writerow(col_names)

    for activity in root.getchildren():
        activity_level_data = activity_data(activity)

        policy_markers = activity.xpath("policy-marker")
        policy_marker_vocabs = []
        policy_marker_codes = []
        policy_marker_sigs = []
        for pol_mark in policy_markers:
            try:
                pol_mark_vocab = str(pol_mark.attrib['vocabulary'])
            except (IndexError, KeyError):
                pol_mark_vocab = ""
            policy_marker_vocabs.append(pol_mark_vocab)
            try:
                pol_mark_code = str(pol_mark.attrib['code'])
            except (IndexError, KeyError):
                pol_mark_code = ""
            policy_marker_codes.append(pol_mark_code)
            try:
                pol_mark_sig = str(pol_mark.attrib['significance'])
            except (IndexError, KeyError):
                pol_mark_sig = ""
            policy_marker_sigs.append(pol_mark_sig)
        policy_marker_vocab = ";".join(policy_marker_vocabs)
        policy_marker_code = ";".join(policy_marker_codes)
        policy_marker_sig = ";".join(policy_marker_sigs)
        activity_level_data.append(policy_marker_vocab)
        activity_level_data.append(policy_marker_code)
        activity_level_data.append(policy_marker_sig)

        try:
            activity_scope = activity.xpath("activity-scope")[0].attrib["code"]
        except (IndexError, KeyError):
            activity_scope = ""
        activity_level_data.append(activity_scope)

        post_budget_activity_level_data = []

        related_activities = activity.xpath("related-activity")
        related_activity_ids = []
        related_activity_types = []
        for rel_act in related_activities:
            try:
                rel_act_id = str(rel_act.attrib['ref'])
            except (IndexError, KeyError):
                rel_act_id = ""
            related_activity_ids.append(rel_act_id)
            try:
                rel_act_type = str(rel_act.attrib['type'])
            except (IndexError, KeyError):
                rel_act_type = ""
            related_activity_types.append(rel_act_type)
        related_activity_id = ";".join(related_activity_ids)
        related_activity_type = ";".join(related_activity_types)
        post_budget_activity_level_data.append(related_activity_id)
        post_budget_activity_level_data.append(related_activity_type)

        contact_infos = activity.xpath("contact-info")
        contact_info_types = []
        contact_info_orgs = []
        contact_info_depts = []
        contact_info_names = []
        contact_info_titles = []
        contact_info_phones = []
        contact_info_emails = []
        contact_info_sites = []
        contact_info_addresses = []
        for c_info in contact_infos:
            try:
                c_info_type = str(c_info.attrib['type'])
            except (IndexError, KeyError):
                c_info_type = ""
            contact_info_types.append(c_info_type)
            try:
                c_info_org = str(c_info.xpath("organisation/narrative")[0].text)
            except (IndexError, KeyError):
                c_info_org = ""
            contact_info_orgs.append(c_info_org)
            try:
                c_info_dept = str(c_info.xpath("department/narrative")[0].text)
            except (IndexError, KeyError):
                c_info_dept = ""
            contact_info_depts.append(c_info_dept)
            try:
                c_info_name = str(c_info.xpath("person-name/narrative")[0].text)
            except (IndexError, KeyError):
                c_info_name = ""
            contact_info_names.append(c_info_name)
            try:
                c_info_title = str(c_info.xpath("job-title/narrative")[0].text)
            except (IndexError, KeyError):
                c_info_title = ""
            contact_info_titles.append(c_info_title)
            try:
                c_info_phone = str(c_info.xpath("telephone")[0].text)
            except (IndexError, KeyError):
                c_info_phone = ""
            contact_info_phones.append(c_info_phone)
            try:
                c_info_email = str(c_info.xpath("email")[0].text)
            except (IndexError, KeyError):
                c_info_email = ""
            contact_info_emails.append(c_info_email)
            try:
                c_info_site = str(c_info.xpath("website")[0].text)
            except (IndexError, KeyError):
                c_info_site = ""
            contact_info_sites.append(c_info_site)
            try:
                c_info_add = str(c_info.xpath("mailing-address/narrative")[0].text)
            except (IndexError, KeyError):
                c_info_add = ""
            contact_info_addresses.append(c_info_add)
        contact_info_type = ";".join(contact_info_types)
        contact_info_org = ";".join(contact_info_orgs)
        contact_info_dept = ";".join(contact_info_depts)
        contact_info_name = ";".join(contact_info_names)
        contact_info_title = ";".join(contact_info_titles)
        contact_info_phone = ";".join(contact_info_phones)
        contact_info_email = ";".join(contact_info_emails)
        contact_info_site = ";".join(contact_info_sites)
        contact_info_address = ";".join(contact_info_addresses)
        post_budget_activity_level_data.append(contact_info_type)
        post_budget_activity_level_data.append(contact_info_org)
        post_budget_activity_level_data.append(contact_info_dept)
        post_budget_activity_level_data.append(contact_info_name)
        post_budget_activity_level_data.append(contact_info_title)
        post_budget_activity_level_data.append(contact_info_phone)
        post_budget_activity_level_data.append(contact_info_email)
        post_budget_activity_level_data.append(contact_info_site)
        post_budget_activity_level_data.append(contact_info_address)

        budgets = activity.xpath("budget")
        for budget in budgets:
            budget_level_data = []

            try:
                budget_type = budget.attrib['type']
            except (IndexError, KeyError):
                budget_type = ""
            budget_level_data.append(budget_type)

            try:
                budget_status = budget.attrib['status']
            except (IndexError, KeyError):
                budget_status = ""
            budget_level_data.append(budget_status)

            try:
                budget_period_start = budget.xpath("period-start")[0].attrib['iso-date']
            except (IndexError, KeyError):
                budget_period_start = ""
            budget_level_data.append(budget_period_start)

            try:
                budget_period_end = budget.xpath("period-end")[0].attrib['iso-date']
            except (IndexError, KeyError):
                budget_period_end = ""
            budget_level_data.append(budget_period_end)

            try:
                budget_value = budget.xpath("value")[0].text
            except (IndexError, KeyError):
                budget_value = ""
            budget_level_data.append(budget_value)

            try:
                budget_value_date = budget.xpath("value")[0].attrib['value-date']
            except (IndexError, KeyError):
                budget_value_date = ""
            budget_level_data.append(budget_value_date)

            try:
                budget_value_currency = budget.xpath("value")[0].attrib['currency']
            except (IndexError, KeyError):
                budget_value_currency = ""
            budget_level_data.append(budget_value_currency)

            cw.writerow(activity_level_data + budget_level_data + post_budget_activity_level_data)

    output = make_response(buffer_wrapper.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename={}_budgets.csv".format(original_basename)
    output.headers["Content-type"] = "text/csv"
    return output


if __name__ == '__main__':
    webbrowser.open("http://localhost:5000")
    app.run(threaded=True)
