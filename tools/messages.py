from email.message import Message


MESSAGES = {
    "ACCOUNT": {
    },
    "AUTHOR": {
    },
    "BOOK": {
        400: 'Invalid Request User Not Found.',
        402: 'Unknown Email User.',
        403: 'Please Verify Your Email to Get Login.',
        405: 'Please login first',
        406: 'Turn on your writer mode first',
        500: 'Server Issue.',
        201: 'chapter doesnt exist',
        202: 'To Unlock the new chapter, You have to earn coins. So start reading free books or purchase coins',
        203: 'Kindly Select the appropriate book',
        204: 'Chapter is already unlocked',
        205: 'Successfully unlock the chapter',
        206: 'Chapter is already unlocked',
        207: 'You dont have enough coins. Earned them or Buy coins',
        208: 'Kindly create the profile with coins',
        209: 'No Such user exist. Kindly login first or Server issue',
        210: 'Book is successfully bookmarked.',
        211: 'Bookmark is successfully removed.',
        212: 'Book does not exist. You cannot bookmark this.'
    },
}
