import requests


def download_reference_from_redcap(api_url, api_token,report_id = "27", form_name="biorepository"):
    """
    Helper function from GUI. Downloads reference data directly from REDCap via API.

    Args:
        api_url (str): The REDCap API endpoint URL
        api_token (str): Your REDCap API token
        form_name (str): The name of the REDCap instrument to export

    Returns:
        records List[Dict]: A list of flat REDCap records
    """

    data = {
        'token': api_token,
        'content': 'report',
        'format': 'json',
        'report_id': report_id,
        'csvDelimiter': '',
        'rawOrLabel': 'raw',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'returnFormat': 'json'
    }
        
    #EAFP style
    try:
        response = requests.post(api_url, data=data, timeout=20)

        # API communication errors
        if response.status_code != 200:
            raise Exception(f"REDCap API returned status code {response.status_code}: {response.text}")

        # JSON decode errors 
        try:
            records = response.json()
        except Exception:
            raise Exception("Could not decode JSON returned from REDCap. Response was:\n" + response.text)

        if not isinstance(records, list):
            raise Exception("Unexpected API response format. Expected list of records.")

        print(f"Successfully downloaded {len(records)} records from REDCap.")
        return records

    except requests.exceptions.ConnectTimeout:
        raise Exception("Connection timed out while contacting REDCap API.")
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to REDCap. Check VPN, URL, or internet.")
    except Exception as e:
        raise Exception(f"REDCap API error: {str(e)}")