import json


def gen_review_request_payloader(place_id, page, count_per_page):
    req = [{
        "operationName": "getVisitorReviews",
        "variables": {
            "input": {
            "businessId": place_id,
            "businessType": "restaurant",
            "item": "0",
            "bookingBusinessId": "75411",
            "page": page,
            "display": count_per_page,
            "isPhotoUsed": False,
            "includeContent": True,
            "getAuthorInfo": True,
            "includeReceiptPhotos": True,
            "cidList": [
                "220036",
                "220038",
                "220081",
                "220804",
                "1004760",
                "1004452"
            ],
            "sort": "recent"
            },
            "id": "676217924"
        },
        "query": "query getVisitorReviews($input: VisitorReviewsInput) {  visitorReviews(input: $input) {    items {      id      status      author {        id        nickname        from        imageUrl        objectId        url        review {          totalCount          imageCount          avgRating          __typename        }        theme {          totalCount          __typename        }        __typename      }      body      thumbnail      media {        type        thumbnail        class        __typename      }      tags      status      visitCount      viewCount      visited      created      reply {        editUrl        body        editedBy        created        replyTitle        __typename      }      originType      item {        name        code        options        __typename      }      language      highlightOffsets      apolloCacheId      translatedText      businessName      showBookingItemName      showBookingItemOptions      bookingItemName      bookingItemOptions      votedKeywords {        code        iconUrl        iconCode        displayName        __typename      }      userIdno      isFollowing      followerCount      followRequested      loginIdno      __typename    }    starDistribution {      score      count      __typename    }    hideProductSelectBox    total    showRecommendationSort    __typename  }}"
    }]
    
    return json.dumps(req)

