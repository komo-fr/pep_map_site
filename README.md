# PEP Map Site
https://komo-fr.github.io/pep_map_site/

## What is this?
"PEP Map Site" is web pages that visualizes the reference relation between PEPs (Python Enhancement Proposals).    
Let's enter the PEP number in the left text box.   
Then you can see the following information.   
1. Which PEPs do link that PEP?
2. Which PEPs are linked from that PEP?

<img src="https://komo-fr.github.io/pep_map_site/image/pep_map_timeline_capture.png" alt="PEP Map| Timeline " title="PEP Map | Timeline">

## Note
- How to get the reference relation between PEPs:
	+ Whether reference relation exists or not is judged based on `<a>` tag. Therefore, it isn't possible to deal with the cases which are not linked even if mentioning other PEP.
	+ The visualized data isn't the latest version since scraping process isn't performed periodically (This will be resolved in the near future). Please check the data acquisition date with "Data as of ..." in the red in the center of the screen.
<img src="https://komo-fr.github.io/pep_map_site/image/data_as_of.png" alt="" title="">
- How to look at the time series plot:
	+ color: The color of the node means PEP's Status. For PEP status, refer to [PEP 1](https://www.python.org/dev/peps/pep-0001/).
	+ date (x axis): The value of the "Created" field for each PEP.
		* According to PEP 1, the "Created" field seems to be a required item. However, in fact there are PEPs that "Created" field is empty. If "Created" is empty, it is not displayed on the time series plot.


If you find funny English, I'd be happy to tell me in issue 😆
(へんな英語見つけたらIssueで教えてね)
