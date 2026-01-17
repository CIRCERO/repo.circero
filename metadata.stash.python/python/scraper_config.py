def configure_scraped_details(details, settings):
    """Configure scraped details based on addon settings"""
    details = _configure_tags(details, settings)
    details = _configure_rating(details, settings)
    return details

def _configure_tags(details, settings):
    """Include or exclude tags based on settings"""
    if not settings.getSettingBool('include_tags'):
        if 'tag' in details['info']:
            del details['info']['tag']
    return details

def _configure_rating(details, settings):
    """Configure rating display"""
    if not settings.getSettingBool('include_rating'):
        if 'rating' in details['info']:
            del details['info']['rating']
    return details
