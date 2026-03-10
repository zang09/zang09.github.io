// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "About",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "Publications",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-honors-amp-awards",
          title: "Honors &amp; Awards",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/honors_and_awards/";
          },
        },{id: "post-google-gemini-updates-flash-1-5-gemma-2-and-project-astra",
        
          title: 'Google Gemini updates: Flash 1.5, Gemma 2 and Project Astra <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "We’re sharing updates across our Gemini family of models and a glimpse of Project Astra, our vision for the future of AI assistants.",
        section: "Posts",
        handler: () => {
          
            window.open("https://blog.google/technology/ai/google-gemini-update-flash-ai-assistant-io-2024/", "_blank");
          
        },
      },{id: "post-displaying-external-posts-on-your-al-folio-blog",
        
          title: 'Displaying External Posts on Your al-folio Blog <svg width="1.2rem" height="1.2rem" top=".5rem" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><path d="M17 13.5v6H5v-12h6m3-3h6v6m0-6-9 9" class="icon_svg-stroke" stroke="#999" stroke-width="1.5" fill="none" fill-rule="evenodd" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.open("https://medium.com/@al-folio/displaying-external-posts-on-your-al-folio-blog-b60a1d241a0a?source=rss-17feae71c3c4------2", "_blank");
          
        },
      },{id: "honors_and_awards-3rd-award-future-robot-idea-presentation",
          title: '3rd Award, Future-Robot Idea Presentation',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2016_kiro/";
            },},{id: "honors_and_awards-winner-robocup-korea",
          title: 'Winner, RoboCup Korea',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2017_robocup_korea/";
            },},{id: "honors_and_awards-4th-place-robocup-iran",
          title: '4th Place, RoboCup Iran',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2017_robocup_iran/";
            },},{id: "honors_and_awards-winner-irc-intelligence-humanoid-robot-sports",
          title: 'Winner, IRC (Intelligence Humanoid Robot Sports)',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2017_irc/";
            },},{id: "honors_and_awards-achievement-award-spread-the-name-throughout-the-year",
          title: 'Achievement Award (Spread the name throughout the year)',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2017_kwangwoon/";
            },},{id: "honors_and_awards-3rd-place-robocup-canada",
          title: '3rd Place, RoboCup Canada',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2018_robocup_canada/";
            },},{id: "honors_and_awards-2nd-place-irc-intelligence-humanoid-robot-sports",
          title: '2nd Place, IRC – Intelligence Humanoid Robot Sports',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2018_irc/";
            },},{id: "honors_and_awards-3rd-place-r-biz-challenge-turtlebot3-autorace",
          title: '3rd Place, R-BIZ Challenge – Turtlebot3 Autorace',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2018_rviz/";
            },},{id: "honors_and_awards-outstanding-mentor-samsung-electronics-junior-software-creation-contest",
          title: 'Outstanding Mentor (Samsung Electronics Junior Software Creation Contest)',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2019_samsung/";
            },},{id: "honors_and_awards-snu-ai-fellowship-m-s-program",
          title: 'SNU AI Fellowship (M.S. Program)',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2023_ms_scholar/";
            },},{id: "honors_and_awards-m-s-research-funding",
          title: 'M.S. Research Funding',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2024_ms_funding/";
            },},{id: "honors_and_awards-jeonghun-foundation-ph-d-scholarship",
          title: 'Jeonghun Foundation Ph.D. Scholarship',
          description: "",
          section: "Honors_and_awards",handler: () => {
              window.location.href = "/honors_and_awards/2026_phd_scholar/";
            },},{id: "news-funded-by-the-korean-ministry-of-education-awarded-to-750-master-s-students-nationwide",
          title: 'Funded by the Korean Ministry of Education, awarded to 750 master’s students nationwide....',
          description: "",
          section: "News",},{id: "news-our-paper-on-3dgs-densification-sampling-has-been-accepted-to-neurips-2025",
          title: 'Our paper on 3DGS densification sampling has been accepted to NeurIPS 2025!',
          description: "",
          section: "News",},{id: "news-our-paper-on-targetless-lidar-camera-calibration-has-been-accepted-to-ra-l-2026",
          title: 'Our paper on targetless LiDAR–camera calibration has been accepted to RA-L 2026!',
          description: "",
          section: "News",},{id: "news-tlc-calib-will-be-presented-at-icra-2026",
          title: 'TLC-Calib will be presented at ICRA 2026!',
          description: "",
          section: "News",},{id: "news-new-selected-as-a-jeonghun-foundation-scholar-for-ph-d-studies",
          title: 'NEW! Selected as a Jeonghun Foundation Scholar for Ph.D. studies.',
          description: "",
          section: "News",},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%68%61%65%62%65%6F%6D.%6A%75%6E%67@%73%6E%75.%61%63.%6B%72", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/zang09", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/haebeom-jung-867b99212/", "_blank");
        },
      },{
        id: 'social-rss',
        title: 'RSS Feed',
        section: 'Socials',
        handler: () => {
          window.open("/feed.xml", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=iQRTLHwAAAAJ", "_blank");
        },
      },{
        id: 'social-my_cv',
        title: 'My_cv',
        section: 'Socials',
        handler: () => {
          window.open("", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
