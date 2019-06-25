# -*- coding: utf-8 -*-
"""
Created on Fri May 24 12:18:48 2019

name: AnilistAPI
description: To interact with the anilist API.

@author: nxf52810
"""

import requests

# Here we define our query as a multi-line string
animeData = '''
query animeData($animeID: Int, $hits: Int, $info: Boolean = false, $multi: Boolean = false, $page: Int, $search: String) {
  Page(page: $page, perPage: $hits) @include(if: $multi) {
    pageInfo {
      currentPage
      lastPage
      hasNextPage
    }
    media(id: $animeID, search: $search, type: ANIME) {
      ...anime
    }
  }
  Media(id: $animeID, type: ANIME) @skip(if: $multi) {
    ...anime
  }
}

fragment anime on Media {
  id
  title {
    userPreferred
  }
  ...information @include(if: $info)
}

fragment information on Media {
  coverImage {
    large
  }
  duration
  episodes
}
'''

userData = '''
query userData($animeID: Int, $username: String) {
  MediaList(userName: $username, mediaId: $animeID) {
    startedAt {
      year
      month
      day
    }
    completedAt {
      year
      month
      day
    }
  }
}

'''

'''
#List of variables

animeID: Int. The id of the show you're retrieving information of
hits: Int. Number of hits you want to recieve per page
info: Boolean, Default false. Whether to get the episode count, duration and image of the show.
multi: Boolean, Default false. Whether to recieve a list of returns.
page: Int. The part of the list of returns you want to recieve.
search: String. The search keywords.
username: The username to be querried for list entries
'''

# Here we define the API Url
url = 'https://graphql.anilist.co'

def get_anime_data(animeID):
    dataVariables = {
            'info': True,
            'multi': False,
    		}
    dataVariables['animeID'] = animeID
    # Make the HTTP Api request
    try:
        response = requests.post(url, json={'query': animeData, 'variables': dataVariables}).json()
    except ConnectionError:
        return None
    if response['data']['Media'] is None:
        return None
    else:
        return(response['data']['Media'])
        
def get_user_data(animeID, username):
    dataVariables = {}
    dataVariables['animeID'] = animeID
    dataVariables['username'] = username
    # Make the HTTP Api request
    try:
        response = requests.post(url, json={'query': userData, 'variables': dataVariables}).json()
    except ConnectionError:
        return None
    if response['data']['MediaList'] is None:
        return None
    else:
        return(response['data']['MediaList'])