"""Geographical hints and curated communities for opt-in Reddit discovery.

A subreddit associated with a place is NOT evidence that its posters live there.
"""

STATES = {
    "Alabama": ("AL", "Birmingham", "Montgomery"),
    "Alaska": ("AK", "Anchorage", "Fairbanks"),
    "Arizona": ("AZ", "Phoenix", "Tucson"),
    "Arkansas": ("AR", "Little Rock", "Fayetteville"),
    "California": ("CA", "Los Angeles", "San Francisco", "San Diego", "Sacramento", "Bay Area"),
    "Colorado": ("CO", "Denver", "Boulder"),
    "Connecticut": ("CT", "Hartford", "New Haven"),
    "Delaware": ("DE", "Wilmington", "Dover"),
    "Florida": ("FL", "Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale"),
    "Georgia": ("GA", "Atlanta", "Savannah"),
    "Hawaii": ("HI", "Honolulu", "Maui"),
    "Idaho": ("ID", "Boise", "Idaho Falls"),
    "Illinois": ("IL", "Chicago", "Springfield"),
    "Indiana": ("IN", "Indianapolis", "Fort Wayne"),
    "Iowa": ("IA", "Des Moines", "Cedar Rapids"),
    "Kansas": ("KS", "Wichita", "Topeka"),
    "Kentucky": ("KY", "Louisville", "Lexington"),
    "Louisiana": ("LA", "New Orleans", "Baton Rouge"),
    "Maine": ("ME", "Portland Maine", "Bangor"),
    "Maryland": ("MD", "Baltimore", "Annapolis"),
    "Massachusetts": ("MA", "Boston", "Cambridge"),
    "Michigan": ("MI", "Detroit", "Ann Arbor"),
    "Minnesota": ("MN", "Minneapolis", "Saint Paul"),
    "Mississippi": ("MS", "Jackson Mississippi", "Gulfport"),
    "Missouri": ("MO", "St Louis", "Kansas City"),
    "Montana": ("MT", "Billings", "Missoula"),
    "Nebraska": ("NE", "Omaha", "Lincoln"),
    "Nevada": ("NV", "Las Vegas", "Reno"),
    "New Hampshire": ("NH", "Manchester NH", "Concord"),
    "New Jersey": ("NJ", "Newark", "Jersey City"),
    "New Mexico": ("NM", "Albuquerque", "Santa Fe"),
    "New York": ("NY", "New York City", "Brooklyn", "Buffalo", "Albany"),
    "North Carolina": ("NC", "Charlotte", "Raleigh", "Durham"),
    "North Dakota": ("ND", "Fargo", "Bismarck"),
    "Ohio": ("OH", "Columbus", "Cleveland", "Cincinnati"),
    "Oklahoma": ("OK", "Oklahoma City", "Tulsa"),
    "Oregon": ("OR", "Portland Oregon", "Eugene"),
    "Pennsylvania": ("PA", "Philadelphia", "Pittsburgh"),
    "Rhode Island": ("RI", "Providence"),
    "South Carolina": ("SC", "Charleston", "Columbia SC"),
    "South Dakota": ("SD", "Sioux Falls", "Rapid City"),
    "Tennessee": ("TN", "Nashville", "Memphis", "Knoxville"),
    "Texas": ("TX", "Dallas", "Houston", "Austin", "San Antonio", "Fort Worth"),
    "Utah": ("UT", "Salt Lake City", "Provo"),
    "Vermont": ("VT", "Burlington Vermont", "Montpelier"),
    "Virginia": ("VA", "Richmond", "Virginia Beach", "Arlington"),
    "Washington": ("WA", "Seattle", "Tacoma", "Spokane"),
    "West Virginia": ("WV", "Charleston WV", "Morgantown"),
    "Wisconsin": ("WI", "Milwaukee", "Madison", "Green Bay"),
    "Wyoming": ("WY", "Cheyenne", "Laramie"),
    "District of Columbia": ("DC", "Washington DC"),
}

# Keep curated entries small, reproducible, and editable. Missing/inaccessible
# subs are skipped with a user-visible warning.
LOCAL_SUBS = {
    "California": ["california", "LosAngeles", "bayarea", "sandiego", "Sacramento"],
    "New York": ["newyorkcity", "nyc", "Buffalo", "Albany"],
    "Texas": ["texas", "Dallas", "houston", "Austin", "sanantonio"],
    "Florida": ["florida", "Miami", "orlando", "tampa", "jacksonville"],
    "Illinois": ["illinois", "chicago"],
    "Massachusetts": ["massachusetts", "boston"],
    "Pennsylvania": ["Pennsylvania", "philadelphia", "pittsburgh"],
    "Washington": ["Washington", "Seattle"],
    "Colorado": ["Colorado", "Denver"],
    "Georgia": ["Georgia", "Atlanta"],
    "Arizona": ["arizona", "phoenix", "Tucson"],
    "Ohio": ["Ohio", "Columbus", "Cleveland", "cincinnati"],
    "Michigan": ["Michigan", "Detroit", "AnnArbor"],
    "North Carolina": ["NorthCarolina", "Charlotte", "raleigh"],
    "Wisconsin": ["wisconsin", "milwaukee", "madisonwi"],
    "Minnesota": ["minnesota", "Minneapolis", "TwinCities"],
    "Oregon": ["oregon", "Portland"],
    "Tennessee": ["Tennessee", "nashville", "memphis"],
    "Nevada": ["Nevada", "vegas", "Reno"],
    "Louisiana": ["Louisiana", "NewOrleans"],
    "New Jersey": ["newjersey", "jerseycity"],
    "Maryland": ["maryland", "baltimore"],
    "Indiana": ["Indiana", "indianapolis"],
    "Missouri": ["missouri", "StLouis", "kansascity"],
    "Utah": ["Utah", "SaltLakeCity"],
    "Oklahoma": ["oklahoma", "okc", "tulsa"],
}

SPORTS_SUBS = {
    "NFL": ["nfl"], "NBA": ["nba"], "MLB": ["baseball", "mlb"],
    "NHL": ["hockey"], "College sports": ["CFB", "CollegeBasketball"],
    "Soccer": ["soccer", "MLS"],
}

TEAM_SUBS = {
    "California": {
        "NFL": ["49ers", "LosAngelesRams", "Chargers"],
        "NBA": ["lakers", "warriors", "LAClippers", "kings"],
        "MLB": ["Dodgers", "SFGiants", "Padres", "angelsbaseball", "OaklandAthletics"],
        "NHL": ["losangeleskings", "AnaheimDucks", "SanJoseSharks"],
        "Soccer": ["LAFC", "LAGalaxy", "SJEarthquakes"],
    },
    "New York": {
        "NFL": ["buffalobills", "NYGiants", "nyjets"],
        "NBA": ["NYKnicks", "GoNets"],
        "MLB": ["NYYankees", "NewYorkMets"],
        "NHL": ["rangers", "NewYorkIslanders", "sabres"],
    },
    "Texas": {
        "NFL": ["cowboys", "Texans"], "NBA": ["Mavericks", "rockets", "NBASpurs"],
        "MLB": ["TexasRangers", "Astros"], "NHL": ["DallasStars"],
    },
    "Florida": {
        "NFL": ["miamidolphins", "buccaneers", "Jaguars"],
        "NBA": ["heat", "OrlandoMagic"], "MLB": ["tampabayrays", "letsgofish"],
        "NHL": ["FloridaPanthers", "TampaBayLightning"],
    },
    "Illinois": {
        "NFL": ["CHIBears"], "NBA": ["chicagobulls"],
        "MLB": ["CHICubs", "whitesox"], "NHL": ["hawks"],
    },
    "Massachusetts": {
        "NFL": ["Patriots"], "NBA": ["bostonceltics"],
        "MLB": ["redsox"], "NHL": ["BostonBruins"],
    },
    "Pennsylvania": {
        "NFL": ["eagles", "steelers"], "NBA": ["sixers"],
        "MLB": ["phillies", "buccos"], "NHL": ["flyers", "penguins"],
    },
    "Washington": {
        "NFL": ["Seahawks"], "MLB": ["Mariners"],
        "NHL": ["SeattleKraken"], "Soccer": ["SoundersFC"],
    },
    "Colorado": {
        "NFL": ["DenverBroncos"], "NBA": ["denvernuggets"],
        "MLB": ["ColoradoRockies"], "NHL": ["ColoradoAvalanche"],
    },
    "Georgia": {"NFL": ["falcons"], "NBA": ["AtlantaHawks"], "MLB": ["Braves"]},
    "Arizona": {"NFL": ["AZCardinals"], "NBA": ["suns"], "MLB": ["azdiamondbacks"], "NHL": []},
    "Ohio": {"NFL": ["Browns", "bengals"], "NBA": ["clevelandcavs"], "MLB": ["ClevelandGuardians", "Reds"], "NHL": ["BlueJackets"]},
    "Michigan": {"NFL": ["detroitlions"], "NBA": ["DetroitPistons"], "MLB": ["motorcitykitties"], "NHL": ["DetroitRedWings"]},
    "North Carolina": {"NFL": ["panthers"], "NBA": ["CharlotteHornets"], "NHL": ["canes"]},
    "Wisconsin": {"NFL": ["GreenBayPackers"], "NBA": ["MkeBucks"], "MLB": ["Brewers"]},
    "Minnesota": {"NFL": ["minnesotavikings"], "NBA": ["timberwolves"], "MLB": ["minnesotatwins"], "NHL": ["wildhockey"]},
    "Oregon": {"NBA": ["ripcity"], "Soccer": ["timbers"]},
    "Tennessee": {"NFL": ["Tennesseetitans"], "NBA": ["memphisgrizzlies"], "NHL": ["Predators"]},
    "Nevada": {"NFL": ["raiders"], "NHL": ["goldenknights"]},
    "Louisiana": {"NFL": ["Saints"], "NBA": ["NOLAPelicans"]},
    "New Jersey": {"NHL": ["devils"]},
    "Maryland": {"NFL": ["ravens"], "MLB": ["orioles"]},
    "Indiana": {"NFL": ["Colts"], "NBA": ["pacers"]},
    "Missouri": {"NFL": ["KansasCityChiefs"], "MLB": ["KCroyals", "Cardinals"], "NHL": ["stlouisblues"]},
    "Utah": {"NBA": ["UtahJazz"], "NHL": ["UtahMammoth"]},
    "Oklahoma": {"NBA": ["Thunder"]},
    "District of Columbia": {"NFL": ["Commanders"], "NBA": ["washingtonwizards"], "MLB": ["Nationals"], "NHL": ["caps"]},
}

CATEGORIES = {
    "Sports": ["All sports", "NFL", "NBA", "MLB", "NHL", "College sports", "Soccer"],
    "Entertainment": ["All entertainment", "Movies", "Television", "Music", "Celebrities"],
    "Technology": ["All technology", "AI", "Gaming", "Consumer tech"],
    "News": ["All news", "Politics", "Business", "Local news"],
}

GLOBAL_SUBS = {
    "Entertainment": {
        "All entertainment": ["entertainment", "popculturechat", "movies", "television", "Music"],
        "Movies": ["movies", "boxoffice", "MovieDetails"],
        "Television": ["television", "TV", "popculturechat"],
        "Music": ["Music", "popheads", "hiphopheads"],
        "Celebrities": ["popculturechat", "Fauxmoi", "entertainment"],
    },
    "Technology": {
        "All technology": ["technology", "gadgets", "technews"],
        "AI": ["artificial", "MachineLearning", "technology"],
        "Gaming": ["gaming", "Games", "pcgaming"],
        "Consumer tech": ["gadgets", "technology", "Android"],
    },
    "News": {
        "All news": ["news", "worldnews", "inthenews"],
        "Politics": ["politics", "PoliticalDiscussion"],
        "Business": ["business", "Economics"],
        "Local news": ["news"],
    },
}

KEYWORDS = {
    "NFL": ["nfl", "football", "quarterback", "touchdown", "super bowl", "chiefs"],
    "NBA": ["nba", "basketball", "lakers", "warriors", "knicks", "celtics", "playoffs"],
    "MLB": ["mlb", "baseball", "pitcher", "home run", "world series"],
    "NHL": ["nhl", "hockey", "puck", "goalie", "stanley cup"],
    "College sports": ["college football", "cfb", "ncaa", "college basketball", "march madness"],
    "Soccer": ["soccer", "football club", "mls", "fifa", "world cup"],
    "Movies": ["movie", "film", "cinema", "actor", "box office", "premiere"],
    "Television": ["tv", "television", "series", "season", "streaming", "episode", "show"],
    "Music": ["album", "artist", "music", "concert", "tour", "song", "singer"],
    "Celebrities": ["celebrity", "actor", "singer", "star", "hollywood", "red carpet"],
    "AI": ["ai", "artificial intelligence", "model", "llm"],
    "Gaming": ["gaming", "video game", "console", "game"],
    "Consumer tech": ["phone", "laptop", "tech", "iphone", "android"],
    "Politics": ["politics", "election", "governor", "congress", "senate"],
    "Business": ["business", "jobs", "company", "stock", "economy"],
}


def dedupe(items):
    result, seen = [], set()
    for item in items:
        cleaned = str(item).strip().removeprefix("r/").strip("/")
        if cleaned and cleaned.casefold() not in seen:
            seen.add(cleaned.casefold())
            result.append(cleaned)
    return result


def candidate_subreddits(category, topic, region, custom=None, cap=18):
    """Return candidates plus a source mapping: local, team, global or manual."""
    candidates = []
    def add(subs, source):
        candidates.extend((name, source) for name in subs)
    national = region == "United States (national)"
    if category == "Sports":
        leagues = list(SPORTS_SUBS) if topic == "All sports" else [topic]
        team_by_league = TEAM_SUBS.get(region, {})
        if not national:
            # Keep broad "All sports" searches balanced. Otherwise one state
            # with many franchises can consume every available API slot.
            if topic == "All sports":
                for league in leagues:
                    add(team_by_league.get(league, [])[:2], "team")
            else:
                for league in leagues:
                    add(team_by_league.get(league, []), "team")
            add(LOCAL_SUBS.get(region, [region.replace(" ", "")])[:3], "local")
        for league in leagues:
            add(SPORTS_SUBS.get(league, [])[:1], "global")
        if topic == "All sports":
            add(["sports"], "global")
            if not national:
                for league in leagues:
                    add(team_by_league.get(league, [])[2:], "team")
    else:
        if not national:
            add(LOCAL_SUBS.get(region, [region.replace(" ", "")])[:4], "local")
        add(GLOBAL_SUBS.get(category, {}).get(topic, []), "global")
    # Manual additions get a fair chance even when curated candidates hit cap.
    # 'Manual' sources still require explicit region text for a state filter.
    curated = list(candidates)
    curated_kinds = {name.casefold(): source for name, source in curated}
    candidates = [(name, curated_kinds.get(name.casefold(), "manual")) for name in (custom or [])[:8]] + curated
    result, used = [], set()
    for name, kind in candidates:
        key = name.casefold()
        if key not in used:
            used.add(key)
            result.append({"name": name, "source": kind})
        if len(result) >= cap:
            break
    return result


# High-confidence, non-ambiguous franchise aliases for national sport posts.
# An alias signals a team's geographic association, never the commenter's home.
TEAM_ALIASES = {
    "California": ["lakers", "warriors", "clippers", "dodgers", "padres", "49ers", "chargers", "rams", "angels", "san francisco giants"],
    "New York": ["knicks", "yankees", "mets", "brooklyn nets", "buffalo bills", "new york giants", "new york jets", "new york rangers"],
    "Texas": ["cowboys", "houston texans", "mavericks", "rockets", "spurs", "astros", "dallas stars", "texas rangers"],
    "Florida": ["dolphins", "buccaneers", "jaguars", "orlando magic", "miami heat", "florida panthers", "tampa bay lightning", "rays", "marlins"],
    "Illinois": ["chicago bulls", "chicago bears", "cubs", "white sox", "blackhawks"],
    "Massachusetts": ["celtics", "bruins", "patriots", "red sox"],
    "Pennsylvania": ["sixers", "76ers", "eagles", "steelers", "phillies", "flyers", "penguins", "pirates"],
    "Washington": ["seahawks", "mariners", "seattle kraken", "sounders"],
    "Colorado": ["broncos", "nuggets", "avalanche", "colorado rockies"],
    "Georgia": ["atlanta hawks", "falcons", "braves"],
    "Arizona": ["arizona cardinals", "phoenix suns", "diamondbacks"],
    "Ohio": ["browns", "bengals", "cavaliers", "cleveland guardians", "cincinnati reds", "blue jackets"],
    "Michigan": ["lions", "pistons", "detroit tigers", "red wings"],
    "North Carolina": ["carolina panthers", "charlotte hornets", "hurricanes"],
    "Wisconsin": ["packers", "bucks", "brewers"],
    "Minnesota": ["vikings", "timberwolves", "minnesota twins", "minnesota wild"],
    "Oregon": ["trail blazers", "portland timbers"],
    "Tennessee": ["tennessee titans", "memphis grizzlies", "nashville predators"],
    "Nevada": ["las vegas raiders", "golden knights"],
    "Louisiana": ["new orleans saints", "pelicans"],
    "Maryland": ["baltimore ravens", "orioles"],
    "Indiana": ["colts", "pacers"],
    "Missouri": ["chiefs", "royals", "st louis cardinals", "blues"],
    "Utah": ["utah jazz", "utah mammoth"],
    "Oklahoma": ["oklahoma city thunder"],
    "District of Columbia": ["washington commanders", "wizards", "washington capitals", "nationals"],
}


def sport_entity_phrases(region):
    return TEAM_ALIASES.get(region, [])


def region_phrases(region):
    if region == "United States (national)":
        return []
    aliases = STATES.get(region, ())
    phrases = [region, *aliases[1:]]
    # Two-letter state codes are too ambiguous for free-text matching.
    return [phrase.lower() for phrase in phrases if len(phrase) >= 4]
