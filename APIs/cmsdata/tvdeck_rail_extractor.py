from typing import Dict, List
from tests.androidtv.pages.utility.system_logger import Logger

log = Logger().setup_logger("CMS.RailExtractor")

NATCO_LANGUAGE_MAPPING = {
    "MKT": ["mk", "en_mk", "sq_mk"],
    "AT": ["de", "en_at"],
    "HU": ["hu", "en_hu"],
    "HR": ["hr", "en_hr"],
    "ME": ["me", "sr", "en_me"],
    "PL": ["pl", "en_pl"],
}


class TVDeckRailExtractor:
    def __init__(self):
        self.logger = log

    def extract_enabled_rail_titles(
        self, components_data: Dict, natco: str, primary_language: str = None
    ) -> Dict[str, List[Dict]]:
        try:
            target_languages = (
                [primary_language]
                if primary_language
                else NATCO_LANGUAGE_MAPPING.get(natco.upper(), [])
            )
            if not target_languages:
                self.logger.warning("No language mapping found for NatCo: %s", natco)
                return {}
            items = components_data.get("items", [])
            if not items:
                self.logger.warning("No items found in components data")
                return {}
            result = {
                "natco": natco,
                "total_components": len(items),
                "enabled_components": 0,
                "rails_by_language": {},
                "summary": {},
            }
            for lang in target_languages:
                result["rails_by_language"][lang] = []
            enabled_count = 0
            for item in items:
                if not item.get("is_enabled", False):
                    continue
                enabled_count += 1
                component_info = {
                    "id": item.get("id"),
                    "order": item.get("order"),
                    "template_type": item.get("template_type"),
                    "is_adult": item.get("is_adult", False),
                    "category_id": item.get("category_id"),
                    "languages": {},
                }
                languages_data = item.get("languages", {})
                for lang_code in target_languages:
                    if lang_code in languages_data:
                        lang_data = languages_data[lang_code]
                        component_info["languages"][lang_code] = {
                            "title": lang_data.get("title"),
                            "sub_title": lang_data.get("sub_title"),
                            "cta_title": lang_data.get("cta_title"),
                            "secondary_title": lang_data.get("secondary_title"),
                            "description": lang_data.get("description"),
                        }
                        rail_entry = {
                            "id": item.get("id"),
                            "order": item.get("order"),
                            "title": lang_data.get("title"),
                            "sub_title": lang_data.get("sub_title"),
                            "template_type": item.get("template_type"),
                            "is_adult": item.get("is_adult", False),
                        }
                        result["rails_by_language"][lang_code].append(rail_entry)
            result["enabled_components"] = enabled_count
            for lang_code in target_languages:
                rails = result["rails_by_language"][lang_code]
                result["summary"][lang_code] = {
                    "total_rails": len(rails),
                    "adult_rails": len([r for r in rails if r.get("is_adult")]),
                    "non_adult_rails": len([r for r in rails if not r.get("is_adult")]),
                }
            return result
        except Exception as e:
            self.logger.error("Error extracting rail titles: %s", str(e))
            return {}

    def get_rail_titles_list(
        self, components_data: Dict, natco: str, language: str
    ) -> List[str]:
        try:
            extraction_result = self.extract_enabled_rail_titles(
                components_data, natco, language
            )
            if language in extraction_result.get("rails_by_language", {}):
                return [
                    rail.get("title", "")
                    for rail in extraction_result["rails_by_language"][language]
                    if rail.get("title")
                ]
            return []
        except Exception as e:
            self.logger.error("Error getting rail titles list: %s", str(e))
            return []

    def get_enabled_rails_by_template_type(
        self,
        components_data: Dict,
        natco: str,
        language: str,
        template_type: str = None,
    ) -> List[Dict]:
        try:
            extraction_result = self.extract_enabled_rail_titles(
                components_data, natco, language
            )
            rails = extraction_result.get("rails_by_language", {}).get(language, [])
            if template_type:
                rails = [
                    rail for rail in rails if rail.get("template_type") == template_type
                ]
            return rails
        except Exception as e:
            self.logger.error("Error getting rails by template type: %s", str(e))
            return []

    def get_adult_vs_non_adult_rails(
        self, components_data: Dict, natco: str, language: str
    ) -> Dict[str, List[str]]:
        try:
            extraction_result = self.extract_enabled_rail_titles(
                components_data, natco, language
            )
            rails = extraction_result.get("rails_by_language", {}).get(language, [])
            adult_titles = [
                rail.get("title", "")
                for rail in rails
                if rail.get("is_adult", False) and rail.get("title")
            ]
            non_adult_titles = [
                rail.get("title", "")
                for rail in rails
                if not rail.get("is_adult", False) and rail.get("title")
            ]
            return {"adult": adult_titles, "non_adult": non_adult_titles}
        except Exception as e:
            self.logger.error("Error separating adult/non-adult rails: %s", str(e))
            return {"adult": [], "non_adult": []}

    def print_rail_summary(self, extraction_result: Dict) -> None:
        try:
            natco = extraction_result.get("natco", "Unknown")
            total = extraction_result.get("total_components", 0)
            enabled = extraction_result.get("enabled_components", 0)
            self.logger.info("=== TV Deck Rails Summary for %s ===", natco)
            self.logger.info("Total Components: %s", total)
            self.logger.info("Enabled Components: %s", enabled)
            summary = extraction_result.get("summary", {})
            for lang_code, lang_summary in summary.items():
                self.logger.info("\n--- %s Language ---", lang_code.upper())
                self.logger.info("Total Rails: %s", lang_summary.get("total_rails", 0))
                self.logger.info("Adult Rails: %s", lang_summary.get("adult_rails", 0))
                self.logger.info(
                    "Non-Adult Rails: %s", lang_summary.get("non_adult_rails", 0)
                )
                rails = extraction_result.get("rails_by_language", {}).get(
                    lang_code, []
                )
                if rails:
                    self.logger.info("Rail Titles:")
                    for rail in sorted(rails, key=lambda x: x.get("order", 0)):
                        title = rail.get("title", "No Title")
                        order = rail.get("order", "?")
                        template = rail.get("template_type", "Unknown")
                        adult_flag = " [ADULT]" if rail.get("is_adult") else ""
                        self.logger.info(
                            "  %s. %s (%s)%s", order, title, template, adult_flag
                        )
        except Exception as e:
            self.logger.error("Error printing rail summary: %s", str(e))

    def export_rails_to_dict(
        self, components_data: Dict, natco: str, language: str
    ) -> Dict[str, any]:
        try:
            extraction_result = self.extract_enabled_rail_titles(
                components_data, natco, language
            )
            rails = extraction_result.get("rails_by_language", {}).get(language, [])
            export_data = {
                "natco": natco,
                "language": language,
                "total_enabled_rails": len(rails),
                "rails": [
                    {
                        "order": rail.get("order"),
                        "title": rail.get("title"),
                        "sub_title": rail.get("sub_title"),
                        "template_type": rail.get("template_type"),
                        "is_adult": rail.get("is_adult", False),
                    }
                    for rail in sorted(rails, key=lambda x: x.get("order", 0))
                ],
                "summary": extraction_result.get("summary", {}).get(language, {}),
            }
            return export_data
        except Exception as e:
            self.logger.error("Error exporting rails data: %s", str(e))
            return {}

    def get_rail_titles(self,components: Dict,natco: str,primary_language: str = None) -> Dict[str, list]:
        
        """
        Extract rail titles per language using the same language-selection logic
        as extract_enabled_rail_titles.
        """

        # Determine target languages
        target_languages = (
            [primary_language]
            if primary_language
            else NATCO_LANGUAGE_MAPPING.get(natco.upper(), [])
        )

        if not target_languages:
            return {}

        titles = {lang: [] for lang in target_languages}

        for component in components.get("items", []):
            # Match reference logic: only enabled components
            if not component.get("is_enabled", False):
                continue

            languages = component.get("languages", {})

            for lang_code in target_languages:
                lang_data = languages.get(lang_code)
                if lang_data and lang_data.get("title"):
                    titles[lang_code].append(lang_data["title"])

        # remove empty language keys
        titles = {k: v for k, v in titles.items() if v}

        return titles


def get_rails_for_natco_language(natco: str, language: str) -> List[str]:
    try:
        from tests.androidtv.api.cmsdata.cms_data import CMSApiClient

        cms_client = CMSApiClient(natco=natco)
        components = cms_client.get_tvdeck_components()
        if components:
            extractor = TVDeckRailExtractor()
            return extractor.get_rail_titles_list(components, natco, language)
        return []
    except Exception as e:
        log.error("Error in utility function: %s", str(e))
        return []


def get_all_natco_rails() -> Dict[str, List[str]]:
    natco_language_map = {"MKT": "mk", "AT": "de", "HU": "hu", "HR": "hr", "ME": "me"}
    results = {}
    for natco, language in natco_language_map.items():
        try:
            rails = get_rails_for_natco_language(natco, language)
            results[f"{natco}_{language}"] = rails
            log.info("Retrieved %d rails for %s (%s)", len(rails), natco, language)
        except Exception as e:
            log.error("Error getting rails for %s: %s", natco, str(e))
            results[f"{natco}_{language}"] = []
    return results

def get_all_adult_rails(natco:str,language:str | None = None):
    try:
        from tests.androidtv.api.cmsdata.cms_data_handler import CMSDataHandler
        cms_client = CMSDataHandler()
        components = cms_client.get_tvdeck_components_for_natco(natco)
        if components:
            extractor = TVDeckRailExtractor()
            return extractor.get_rail_titles(components, natco, language)
        return {}
        
    except Exception as e:
        log.error("Error in function: %s", str(e))
        return {}
