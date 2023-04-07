BEGIN TRANSACTION;
INSERT INTO "cmp_fingerprints" ("cmp_name","type","value") VALUES ('OneTrust','raw_html','id="onetrust'),
 ('LiveRamp','text','To provide the best experiences, we and our partners use technologies like cookies to store and/or access device information. Consenting to these technologies will allow us and our partners to process personal data such as browsing behaviour or unique IDs on this site.'),
 ('Quantcast','raw_html','qc-cmp2-consent-info'),
 ('TrustArc','raw_html','truste-'),
 ('Cookiebot','raw_html','CybotCookiebotDialog'),
 ('Cookiebot','raw_html','uc-banner-content'),
 ('Crownpeak','raw_html','_evidon_banner'),
 ('CookieYes','raw_html','cookie-law-info-bar'),
 ('Didomi','raw_html','didomi-notice'),
 ('Osano','raw_html','osano-cm-window'),
 ('CookieYes','raw_html','cky-consent'),
 ('Termly','raw_html','termly-styles'),
 ('DataPrivacyManager','raw_html','hs-eu-cookie-confirmation'),
 ('Ezoic','raw_html','ez-cookie-dialog'),
 ('Google','raw_html','fc-dialog-container');
INSERT INTO "dictionaries" ("name","words","source","date_updated") VALUES ('dialog_ngrams','1:cookies,cookie,track,tracking
2:use cookies,cookies and,cookies to,we use,accept all,any time,at any,you agree,learn more, manage preferences
3:we use cookies,at any time,use cookies and,use cookies to,cookies and similar,use of cookies,learn more about,and our partners,and similar technologies,our cookie policy
4:we use cookies to,use cookies and similar,cookies and similar technologies,you can change your,access information on a,and or access information,at any time by,information on a device,or access information on,store and or access
5:access information on a device,and or access information on,store and or access information,use cookies and similar technologies,ad and content measurement audience,and content measurement audience insights,audience insights and product development,content measurement audience insights and,improve your experience on our,measurement audience insights and product','Manual Input',NULL),
 ('dialog_additional_div_selectors','div[class*="gdpr"]
div[class*="Cookie"]
div[class*="cookie"]
div[class*="Privacy"]
div[class*="privacy"]
div[class*="Policy"]
div[class*="policy"]
div[class*="Consent"]
div[class*="consent"]
div[class*="Notice"]
div[class*="notice"]
div[class*="Dialog"]
div[class*="dialog"]
div[id*="gdpr"]
div[id*="Cookie"]
div[id*="cookie"]
div[id*="Privacy"]
div[id*="privacy"]
div[id*="Policy"]
div[id*="policy"]
div[id*="Consent"]
div[id*="consent"]
div[id*="Notice"]
div[id*="notice"]
div[id*="Dialog"]
div[id*="dialog"]
div[data-project*="cmp"]
div[id*="privacy"]
div[id*="Privacy"]
div[id*="cmp"]','Manual Input',NULL),
 ('dialog_additional_selectors','[class*="gdpr"]
[class*="Cookie"]
[class*="cookie"]
[class*="Privacy"]
[class*="privacy"]
[class*="Policy"]
[class*="policy"]
[class*="Consent"]
[class*="consent"]
[class*="Notice"]
[class*="notice"]
[class*="Dialog"]
[class*="dialog"]
[id*="gdpr"]
[id*="Cookie"]
[id*="cookie"]
[id*="Privacy"]
[id*="privacy"]
[id*="Policy"]
[id*="policy"]
[id*="Consent"]
[id*="consent"]
[id*="Notice"]
[id*="notice"]
[id*="Dialog"]
[id*="dialog"]
[role*="dialog"]','Manual Input',NULL),
 ('clickable_selectors','button 
a
[role=''button'']
input[type=''submit'']
input[type="checkbox"]
span[class*="button"]
span[class*="Button"]
span[class*="btn"]
span[class*="btn"]
[class*="close"]
[class*="Close"]
[class*="button"]
[class*="Button"]
[data-tracking-opt-in-learn-more]
[data-tracking-opt-in-accept]
[class*="settings"]
[id*="custom"]
[id*="accept"]
[class*="settings"]
[class*="custom"]
[class*="accept"]','Manual Input',NULL),
 ('clickable_close_selectors','[class*="close"]
[class*="Close"]
[aria-label*="close"]
[aria-label*="Close"]
svg','Manual Input',NULL),
 ('clickable_preference_slider_selectors','input[type="checkbox"]','Manual Input',NULL);
COMMIT;
