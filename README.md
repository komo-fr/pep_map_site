# PEP Map (α ver)
## What is this?
<a href="https://komo-fr.github.io/pep_map_site/" target="_blank">PEP Map</a> is web pages that **visualizes the reference relation between PEPs** (Python Enhancement Proposals).   
**Timeline:** https://komo-fr.github.io/pep_map_site/timeline.html   
**Network:** https://komo-fr.github.io/pep_map_site/network.html   
 
## Timeline
https://komo-fr.github.io/pep_map_site/timeline.html   
Let's enter the PEP number in the left text box.   
Then you can see the following information.   
1. Which PEPs do link that PEP?
2. Which PEPs are linked from that PEP?

<img src="https://komo-fr.github.io/pep_map_site/image/pep_map_timeline_capture.png" alt="PEP Map| Timeline " title="PEP Map | Timeline">

**Note**
- How to look at the time series plot:
	+ color: The color of the node means PEP's Status. For PEP status, refer to [PEP 1](https://www.python.org/dev/peps/pep-0001/).
	+ date (x axis): The value of the "Created" field for each PEP.
		* According to PEP 1, the "Created" field seems to be a required item. However, in fact there are PEPs that "Created" field is empty. If "Created" is empty, it isn't displayed on the time series plot.
		
## Network
https://komo-fr.github.io/pep_map_site/network.html   

Let's enter the PEP number in the left text box or tap node.   
Then you can see the following information.   
1. Which PEPs do link that PEP?
2. Which PEPs are linked from that PEP?

<img src="https://komo-fr.github.io/pep_map_site/image/network_capture.png" alt="PEP Map| Network" title="PEP Map | Network">

**Note**
- Node size: 
    + The area of the node is proportional to in-degree (the number of other PEP referring to this PEP).
    + if in-degree is 0, the PEP is drawn with 1 / 10 size of PEP that has in-degree is 1.
    + Self loop and PEP 0 (Table of Contents) are not counted.
- Node color:
    + The color of the node means PEP's Status. For PEP status, refer to [PEP 1](https://www.python.org/dev/peps/pep-0001/).
    
## Data
- How to get the reference relation between PEPs:
	+ Whether reference relation exists or not is judged based on `<a>` tag. Therefore, it is **NOT** possible to deal with the cases which aren't linked even if mentioning other PEP.
	+ The visualized data is **NOT** the latest version since scraping process isn't performed periodically (This will be resolved in the near future). Please check the data acquisition date with *"Data as of ..."* in the red in the center of the screen.

If you find mistakes in my English, I'd be happy to tell me in issue 😆   
(へんな英語見つけたらIssueで教えてね)
