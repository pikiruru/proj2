#################################
##### Name: Yizhu Lu    
##### Uniqname:   yizhulu
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import time

BASE_URL="https://www.nps.gov"
CACHE_FILE_NAME ='cache_project2.json'
CACHE_DICT = {}


def load_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILE_NAME,'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def construct_unique_key(baseurl, params):
    ''' constructs a key that is guaranteed to uniquely and 
    repeatably identify an request by its baseurl and params

    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint or website
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    string
        the unique key as a string
    '''
    if params:
        unique_string = []
        connector ="_"
        for key in params.keys():
            unique_string.append(f"{key}_{params[key]}")
        unique_string.sort()
        unique_key = baseurl + connector + connector.join(unique_string)
    else:
        unique_key = baseurl
    return unique_key


def make_url_request_using_cache(url, cache, params):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    
    Parameters
    ----------
    url: string
        The URL for the website
    cache: dict
        The dictionary to save
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
    '''
    unique_key = construct_unique_key(url,params)
    if (unique_key in cache.keys()):
        print("Using cache")
        return cache[unique_key]
    else:
        print("Fetching")
        time.sleep(1)
        cache[unique_key] = requests.get(url,params).text
        save_cache(cache)
        return cache[unique_key]

def make_url_request_using_cache_API(url, cache, params):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.
    
    Parameters
    ----------
    url: string
        The URL for the API endpoint
    cache: dict
        The dictionary to save
    params: dict
        A dictionary of param:value pairs
    
    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
    '''
    unique_key = construct_unique_key(url,params)
    if (unique_key in cache.keys()):
        print("Using cache")
        return cache[unique_key]
    else:
        print("Fetching")
        time.sleep(1)
        cache[unique_key] = requests.get(url,params).json()
        save_cache(cache)
        return cache[unique_key]


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self,category,name,address,zipcode,phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode=zipcode
        self.phone=phone

    def info(self):
        return self.name+" (" +self.category+"): "+ self.address+ " "+self.zipcode


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    response = make_url_request_using_cache(BASE_URL,CACHE_DICT,params=None)
    soup = BeautifulSoup(response, 'html.parser')

    state_list_parent = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
    state_list = state_list_parent.find_all('li')
    final_dict={}
    
    for i in state_list:
        state_key =i.find('a').text
        state_url =i.find('a')['href']
        final_dict[state_key.lower()]=BASE_URL+state_url
    
    return final_dict
       

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    response=make_url_request_using_cache(site_url,CACHE_DICT,params=None)
    soup = BeautifulSoup(response, 'html.parser')
    site_titlecontainer= soup.find('div', class_="Hero-titleContainer clearfix")
    if site_titlecontainer:
        site_name = site_titlecontainer.find('a')
        if site_name:
            site_name= site_name.text
        else:
            site_name='no name'
        site_type = site_titlecontainer.find('span', class_="Hero-designation")
        if site_type:
            site_type=site_type.text
        else:
            site_type = 'no type'
    else:
        site_name='no name'
        site_type='no type'

    site_contact_info = soup.find('div', class_='vcard')
    if site_contact_info:
        site_location = site_contact_info.find('span', itemprop="addressLocality")
        if site_location:
            site_location=site_location.text
        else:
            site_location='no location'       
        site_state = site_contact_info.find('span', itemprop="addressRegion")
        if site_state:
            site_state=site_state.text
        else:
            site_state='no state'
        site_address = site_location+", "+site_state    
        site_zipcode = site_contact_info.find('span', itemprop="postalCode")
        if site_zipcode:
            site_zipcode=site_zipcode.text
        else:
            site_zipcode='no zipcode'   
        site_phone = site_contact_info.find('span', itemprop="telephone")
        if site_phone:
            site_phone=site_phone.text
        else:
            site_phone='no phone'
    else:
        site_address='no address'
        site_zipcode='no zip code'
        site_phone='no phone'
        
    national_site_object = NationalSite(category=site_type.strip(),
                                        name=site_name.strip(),
                                        address=site_address.strip(),
                                        zipcode=site_zipcode.strip(),
                                        phone=site_phone.strip())
    return national_site_object


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    response = make_url_request_using_cache(state_url,CACHE_DICT,params=None)
    soup = BeautifulSoup(response, 'html.parser')
    park_list = soup.find_all('div', class_="col-md-9 col-sm-9 col-xs-12 table-cell list_left")
    
    site_list =[]
    for i in park_list:
        park_url = BASE_URL+i.find('a')['href']
        site_list.append(get_site_instance(park_url))
    return site_list

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    base_url='http://www.mapquestapi.com/search/v2/radius'
    param_dict={
        "key":secrets.API_KEY,
        "origin":site_object.zipcode,
        "radius":10.0,
        "units":'m',
        "maxMatches":10,
        "ambiguities":"ignore",
        "outFormat":'json'
        }
    query_response = make_url_request_using_cache_API(base_url,CACHE_DICT,param_dict)
    return query_response

def print_nearby_places(site_object):
    ''' Use the get_nearby_places function to get site results,
        then get information of maximum 10 nearby places,
        return them in "- <name> (<category>): <street address>, <city name>"
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    list
        a list of 10 nearby places information .
    '''
    district_dict = get_nearby_places(site_object)['searchResults']
    print_list =[]

    for result in district_dict:
        field_info = result['fields']
        dist_name = field_info['name']
        if 'group_sic_code_name' in field_info.keys():
            if field_info['group_sic_code_name'] != "":
                dist_category =field_info['group_sic_code_name']
            else:
                dist_category ='no category'
        else:
            dist_category ='no category'

        if 'address' in field_info.keys():
            if field_info['address'] != "":
                dist_street_address =field_info['address']
            else:
                dist_street_address ='no address'
        else:
            dist_street_address ='no address'
            
        if 'city' in field_info.keys():
            if field_info['city'] != "":
                dist_city =field_info['city']
            else:
                dist_city ='no city'
        else:
            dist_city ='no city'
        each_district= "- "+dist_name+" ("+dist_category+") : "+dist_street_address+", "+dist_city
        print_list.append(each_district)

    return print_list
    

if __name__ == "__main__":

    CACHE_DICT = load_cache()

    input_str1="Enter a state name (e.g. Michigan, michigan) or \"exit\" to quit: "
    input_str2="Choose the number for detail search or \"exit\" or \"back\": "

    response = input(input_str1)
    while (response.lower() != 'exit'):
        response = response.strip().lower()
        state_dict = build_state_url_dict()

        try:
            state_url = state_dict[response]
            site_list = get_sites_for_state(state_url)
            state_title ="List of national sites in "+ response
            print("-"*len(state_title))
            print(state_title)
            print("-"*len(state_title))

            for i in range(len(site_list)):
                print ("["+ f"{i+1}" +"] "+ site_list[i].info())
            print("-"*len(input_str2))
            
            response =input(input_str2) 
            while (response.lower() != 'exit' and response.lower() != 'back'):
                if response.isnumeric()==True:
                    if (int(response)-1) in range(len(site_list)):
                        site_object = site_list[int(response)-1]
                        place_title = "Places near " + str(site_object.name)
                        print_list = print_nearby_places(site_object)
                        print("-"*len(place_title))
                        print(place_title)
                        print("-"*len(place_title))
                        for i in print_list:
                            print(i)
                        print("-"*len(input_str2))
                    else:
                        print("[Error] Invalid input")
                        print("-"*len(input_str2))
                else:
                    print("[Error] Invalid input")
                    print("-"*len(input_str2))
                response = input(input_str2)

            if response.lower() == 'back':
                response=input(input_str1)
                print("-"*len(input_str1))
                continue        
            elif response.lower() == 'exit':
                continue
        except:
            print("[Error] Enter proper state name")
            response = input(input_str1)
            continue
