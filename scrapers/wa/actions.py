import re
from utils.actions import Rule, BaseCategorizer


# http://www.leg.wa.gov/legislature/pages/committeelisting.aspx#
committees_abbrs = {
    u"AGNR": u"Agriculture & Natural Resources",
    # u'APPE': '',
    # u'APPG': '',
    # u'APPH':
    # u'ARED': '',
    u"AWRD": u"Agriculture, Water & Rural Economic Development",
    u"BFS": u"Business & Financial Services",  # u'Early Learning & K-12 Education',
    u"CB": u"Capital Budget",
    u"CDH": u"Community & Economic Development & Housing",
    u"ED": u"Education",  # u'Education Appropriations & Oversight',
    u"EDTI": u"Economic Development, Trade & Innovation",
    u"EDU": u"Education",
    # u'General Government Appropriations & Oversight'
    u"ELHS": u"Early Learning & Human Services",
    u"ENRM": u"Energy, Natural Resources & Marine Waters",
    u"ENV": u"Environment",
    u"ENVI": u"Environment",
    u"EWE": u"Health & Human Services Appropriations & Oversight",
    u"FIHI": u"Financial Institutions, Housing & Insurance",  # u'Health & Long-Term Care',
    u"GO": u"Government Operations, Tribal Relations & Elections",
    u"HCW": u"Health Care & Wellness",
    u"HE": u"Higher Education",
    u"HEA": "Homeowners' Association Act",
    u"HEWD": u"Higher Education & Workforce Development",
    u"HSC": u"Human Services & Corrections",
    u"JUD": u"Judiciary",
    u"JUDI": u"Judiciary",
    u"LCCP": u"Labor, Commerce & Consumer Protection",
    u"LG": u"Local Government",
    u"LWD": u"Labor & Workforce Development",
    # u'NRMW': '',
    u"PSEP": u"Public Safety & Emergency Preparedness",
    u"SGTA": u"State Government & Tribal Affairs",
    u"TEC": u"Technology, Energy & Communications",
    u"TR": u"Transportation",
    u"TRAN": u"Transportation",
    u"WAYS": u"Ways & Means",
}
committee_names = committees_abbrs.values()
committees_rgx = "(%s)" % "|".join(sorted(committee_names, key=len, reverse=True))

# These are regex patterns that map to action categories.
_categorizer_rules = (
    Rule(
        r"yeas, (?P<yes_votes>\d+); nays, (?P<no_votes>\d+); "
        r"absent, (?P<absent_voters>\d+); excused, (?P<excused_voters>\d+)"
    ),
    Rule(r"Committee on (?P<committees>.+?) at \d"),
    Rule(r"(?P<committees>.+?) relieved of further"),
    Rule(r"Passed to (?P<committees>.+?) for \S+ reading"),
    Rule(r"by (?P<committees>.+?) Committee"),
    Rule(r"^Adopted", "passage"),
    Rule(r"^Introduced", "introduction"),
    Rule(r"Third reading, adopted", ["reading-3", "passage"]),
    Rule(r"Prefiled for introduction", "filing"),
    Rule(r"amendment adopted", "amendment-passage"),
    Rule(r"amendment not adopted", "amendment-failure"),
    Rule(r"(?i)third reading, (?P<pass_fail>(passed|failed))", "reading-3"),
    Rule(r"Read first time", "reading-1"),
    Rule(r"(?i)first reading, referred to (?P<committees>.*)\.", "reading-1"),
    Rule(r"(?i)And refer to (?P<committees>.*)", "referral-committee"),
    Rule(r"(?i).* substitute bill substituted.*", "substitution"),
    Rule(r"(?i)chapter (((\d+),?)+) \d+ laws.( .+)?", ""),  # XXX: Thom: Code stuff?
    Rule(r"(?i)effective date \d{1,2}/\d{1,2}/\d{4}.*", ""),
    Rule(
        r"(?i)(?P<committees>\w+) - majority; do pass with amendment\(s\) \
         (but without amendments\(s\))?.*\.",
        "committee-passage-favorable",
        "committee-passage",
    ),
    Rule(
        r"(?i)Executive action taken in the (House|Senate) committee on (?P<committees>.*) \
         (at)? .*\.",
        "",
    ),
    Rule(
        r"(?i)(?P<committees>\w+) \- Majority; do pass .* \(Majority Report\)",
        "passage",
    ),
    Rule(r"(?i)Conference committee appointed.", ""),
    Rule(r"(?i)Conference committee report;", ""),
    Rule(
        r"(?i).+ - Majority; \d+.+ substitute bill be substituted, do pass", "passage"
    ),
    Rule(r"President signed", "passage"),
    Rule(r"Speaker signed", "passage"),
    Rule(
        r"(?i)Signed by (?P<signed_chamber>(Representatives|Senators)) (?P<legislators>.*)",
        "passage",
    ),
    Rule(r"(?i)Referred to (?P<committees>.*)(\.)?"),
    Rule(
        r"(?i)(?P<from_committee>.*) relieved of further consideration. On motion, referred to \
         (?P<committees>.*)",
        "referral-committee",
    ),
    Rule(r"(?i)Governor partially vetoed", "executive-veto-line-item"),
    Rule(r"(?i)Governor vetoed", "executive-veto"),
    Rule(r"(?i)Governor signed", "executive-signature"),
    Rule(r"(?i)Passed final passage;", "passage"),
    Rule(r"(?i)Failed final passage;", "failure"),
    Rule(r"Effective date", "became-law"),
    Rule(r"Chapter .* Laws", "became-law"),
)


class Categorizer(BaseCategorizer):
    rules = _categorizer_rules

    def categorize(self, text):
        """Wrap categorize and add boilerplate committees."""
        attrs = BaseCategorizer.categorize(self, text)
        if "committees" in attrs:
            committees = attrs["committees"]
            for committee in re.findall(committees_rgx, text, re.I):
                if committee not in committees:
                    committees.append(committee)
        return attrs
