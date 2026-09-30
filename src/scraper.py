import json
import os
import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

RAW_KB = [
    {
        "id": "iitk_gen_01",
        "title": "IIT Kanpur Overview & Establishment",
        "category": "General Information",
        "source_url": "https://www.iitk.ac.in/about-us",
        "content": """Indian Institute of Technology Kanpur (IIT Kanpur or IITK) is a premier public technical university located in Kanpur, Uttar Pradesh, India. Established in 1959 under the Institutes of Technology Act, it was declared an Institute of National Importance. 

IIT Kanpur was founded with the assistance of a consortium of nine leading US research universities (including MIT, Caltech, Princeton, Michigan, and UC Berkeley) under the Kanpur Indo-American Programme (KIAP). The institute's motto is 'Tamso ma jyotirgamaya' (Lead me from darkness to light).

The sprawling 1,050-acre green campus is located on the Grand Trunk Road in Kalyanpur, about 16 km west of Kanpur city. IIT Kanpur consistently ranks among the top engineering institutes in India by NIRF and QS World University Rankings."""
    },
    {
        "id": "iitk_acad_01",
        "title": "Academic Programs & Departments at IITK",
        "category": "Academics",
        "source_url": "https://www.iitk.ac.in/doaa/academic-structure",
        "content": """IIT Kanpur offers Undergraduate (B.Tech, B.S.), Postgraduate (M.Tech, M.S. by Research, M.Sc., MBA, M.Des.), and Doctoral (Ph.D.) degree programs across various disciplines:

Departments include:
1. Computer Science and Engineering (CSE)
2. Electrical Engineering (EE)
3. Mechanical Engineering (ME)
4. Biological Sciences and Bioengineering (BSBE)
5. Chemical Engineering (CHE)
6. Civil Engineering (CE)
7. Aerospace Engineering (AE)
8. Materials Science and Engineering (MSE)
9. Sustainable Energy Engineering (SEE)
10. Physics, Chemistry, Mathematics & Statistics
11. Humanities and Social Sciences (HSS)
12. Management Sciences (IME / School of Management)
13. Gangwal School of Medical Sciences and Technology (GSMST)

Academics are administered by the Dean of Academic Affairs (DOAA). The grading system uses a 10-point Cumulative Performance Index (CPI) based on letter grades: A* (10 Outstanding), A (10), B (8), C (6), D (4), E/F (Fail)."""
    },
    {
        "id": "iitk_cse_01",
        "title": "Computer Science & Engineering (CSE) Department",
        "category": "Academics",
        "source_url": "https://www.cse.iitk.ac.in/",
        "content": """The Department of Computer Science and Engineering (CSE) at IIT Kanpur is one of the pioneer computer science departments in India, established in 1984. It offers B.Tech, M.Tech, MS by Research, and Ph.D. degrees.

Key research areas in CSE IITK:
- Artificial Intelligence, Machine Learning, & Natural Language Processing
- Cybersecurity, Cryptography, & C3i Hub (National Centre of Excellence in Cybersecurity)
- Computer Systems, Operating Systems, Compilers, Architecture, & Distributed Systems
- Theoretical Computer Science, Algorithms, & Complexity Theory
- Computer Vision, Graphics, & Robotics

The department features world-class computing facilities, specialized research labs, and notable alumni including N. R. Narayana Murthy (co-founder of Infosys) and Ashoke Sen."""
    },
    {
        "id": "iitk_life_01",
        "title": "Vox Populi - Official Student Media of IIT Kanpur",
        "category": "Student Life & Media",
        "source_url": "https://voxiitk.com/",
        "content": """Vox Populi ('Vox') is the official student-run journalistic and media body of IIT Kanpur. It functions as an independent voice of the student community, covering campus news, investigative reports, opinion articles, interviews with faculty and alumni, and student senate proceedings.

Key features of Vox Populi:
- Campus News: Comprehensive coverage of campus policy updates, academic changes, Gymkhana elections, and festival highlights.
- Vox-Uncensored & Campus Issues: Platform for students to voice concerns on mental health, hostel facilities, mess quality, and academic stress.
- As We Leave (AWL) Series: Special graduation edition featuring reflective farewell articles written by graduating final-year students.
- Orientation Guides: Freshmen guide books detailing campus jargon, academic survival tips, and student body contacts."""
    },
    {
        "id": "iitk_gym_01",
        "title": "Students' Gymkhana & Cultural / Tech Festivals",
        "category": "Student Life & Media",
        "source_url": "https://students.iitk.ac.in/gymkhana/",
        "content": """The Students' Gymkhana is the executive student self-governance body at IIT Kanpur. It is headed by the President, Students' Gymkhana, along with General Secretaries for Cultural Affairs, Science & Technology, Sports, and Academic Affairs (UG & PG).

Major Annual Festivals:
1. Antaragni: One of North India's largest annual cultural festivals, held in October. Features competitions in dance, dramatics, music, fashion show (Ritambhara), literary events, and flagship Pronites (celebrity concerts, international bands).
2. Techkriti: International technical and entrepreneurial festival held in March. Includes robotics, AI hackathons, business plan competitions (Ideas), airshow, and guest talks by Nobel Laureates and industry leaders.
3. Udghosh: Annual inter-collegiate sports festival featuring nationwide competition across athletics, cricket, football, basketball, badminton, chess, and squash.

Active Clubs: Programming Club, Robotics Club, Aeromodelling Club, Electronics Club, Dance Club, Music Club, Dramatics Club (Mana), Fine Arts Club, Literary Society, Astronomy Club, Photography Club."""
    },
    {
        "id": "iitk_hostel_01",
        "title": "Halls of Residence (Hostels) at IIT Kanpur",
        "category": "Facilities & Hostels",
        "source_url": "https://www.iitk.ac.in/dosa/halls-of-residence",
        "content": """IIT Kanpur is a fully residential campus. All undergraduate and postgraduate students reside in state-of-the-art Halls of Residence (Hostels):

Halls List:
- Hall 1 to Hall 14: Boys hostels equipped with single/double occupancy rooms, quad green courtyards, sports courts, and study rooms.
- Girls Hostels: Girls Hostel 1 (GH1), Girls Hostel 2 (GH2), and new GH blocks designed with high security, lush lawns, and modern amenities.
- RA Tower & Married Students Apartments (SBRA): Dedicated housing for postgraduate researchers and married scholars.

Hall Facilities:
- Student-Managed Mess: Every hall has a student-elected Mess Committee managing nutritious veg & non-veg meals.
- Night Canteens & Hall Canteens: Open till 2:00 AM – 3:00 AM serving hot snacks, parathas, noodles, and beverages during late-night study sessions.
- Amenities: 24/7 high-speed LAN/Wi-Fi, reading rooms, computer rooms, TV rooms, music rooms, table tennis, badminton, and volleyball courts in every hall."""
    },
    {
        "id": "iitk_fac_01",
        "title": "PK Kelkar Library & Campus Infrastructure",
        "category": "Facilities & Hostels",
        "source_url": "https://www.iitk.ac.in/pkklib/",
        "content": """The P. K. Kelkar Library (named after IITK's founding director Dr. Purushottam Kashinath Kelkar) is one of the finest academic libraries in Asia:
- Houses over 300,000 volumes of books, research journals, thesis collections, and rare manuscripts.
- Provides 24/7 air-conditioned reading halls during examination periods.
- Subscribes to global digital repositories including IEEE Xplore, ACM Digital Library, SpringerLink, ScienceDirect, and JSTOR.
- Equipped with RFID automated book check-out systems and digital archives.

Other Key Campus Infrastructure:
- Computer Centre (CC): Features high-performance computing (HPC) clusters, campus fiber network infrastructure, and supercomputing grid.
- IITK Airstrip: IIT Kanpur is the only institute in India with its own 1.5 km functional airstrip used for flight testing, aeronautical experiments, and glider rides.
- Health Centre: 24x7 medical clinic with full-time doctors, emergency ward, pharmacy, ambulance services, and specialist consultants.
- Shopping Centre (MT - Main Market): Houses stationery shops, bakery, hair salons, clothes alteration, bike repair, State Bank of India (SBI), Union Bank, and multiple ATMs."""
    },
    {
        "id": "iitk_place_01",
        "title": "Students' Placement Office (SPO) / ICS & Career Statistics",
        "category": "Placements & Internships",
        "source_url": "https://spo.iitk.ac.in/",
        "content": """The Students' Placement Office (SPO), operating under the International Relations and Career Services (ICS), manages campus recruitment and summer internships for IIT Kanpur students.

Placement Highlights:
- Phase 1 Placement Season begins on December 1st each year.
- Over 250+ top global companies visit the campus annually.
- Participating Sectors: Software Engineering, Data Science & AI, Quantitative Finance, Core Engineering, Management Consulting, Product Management, and R&D.
- Top Recruiters: Google, Microsoft, Apple, Amazon, Texas Instruments, Qualcomm, Jane Street, Alphagrep, Graviton Research, Goldman Sachs, McKinsey & Co., BCG, Bain & Co., ISRO, Airbus, Tata Motors.
- Salary Packages: International packages routinely top $200,000 USD (1.5+ Crore INR), while domestic packages reach up to 1.2 Crore INR. Average salaries for CSE and EE graduates consistently range between 25 LPA to 45 LPA."""
    },
    {
        "id": "iitk_research_01",
        "title": "Research, Innovation & SIIC Incubator",
        "category": "Research & Innovation",
        "source_url": "https://siiciitk.com/",
        "content": """IIT Kanpur is a leader in technological innovation, research, and deep-tech entrepreneurship:

Startup Incubation and Innovation Centre (SIIC):
- Established in 2000, SIIC is one of India's oldest and most successful technology incubators.
- Has nurtured over 150+ startups in MedTech, CleanTech, Drones, Artificial Intelligence, Cybersecurity, and AgriTech.
- Key innovations born at IITK include indigenous ventilators during COVID-19, AI drone surveillance systems, and water purification technologies.

Specialized Research Centers:
- National Centre for Flexible Electronics (NCFlexE): Pushing boundaries in printed, flexible, and wearable electronics.
- C3i Hub (Cyber Security Centre of Excellence): National hub dedicated to securing critical infrastructure, blockchain, and cybersecurity defense.
- National Wind Tunnel Facility (NWTF): Advanced aerodynamic research facility with large-scale subsonic wind tunnels used by ISRO and DRDO."""
    }
]

def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def build_knowledge_base(output_path: str = "data/iitk_campus_kb.json") -> List[Dict[str, Any]]:
    """Build and save the structured knowledge base dataset."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    cleaned_kb = []
    for item in RAW_KB:
        cleaned_item = {
            "id": item["id"],
            "title": item["title"],
            "category": item["category"],
            "source_url": item["source_url"],
            "content": clean_text(item["content"])
        }
        cleaned_kb.append(cleaned_item)
    
    # Optionally attempt live scrape enhancement from Vox Populi or IITK portal
    try:
        url = "https://voxiitk.com/"
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            headings = [h.get_text().strip() for h in soup.find_all(["h1", "h2", "h3"]) if len(h.get_text().strip()) > 10][:5]
            if headings:
                cleaned_kb.append({
                    "id": "iitk_vox_live_01",
                    "title": "Vox Populi Live Campus Feed",
                    "category": "Student Life & Media",
                    "source_url": "https://voxiitk.com/",
                    "content": f"Recent stories and features from Vox Populi student journal: {' | '.join(headings)}"
                })
    except Exception as e:
        # Fallback cleanly to curated KB
        pass

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_kb, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully generated knowledge base with {len(cleaned_kb)} entries at: {output_path}")
    return cleaned_kb

if __name__ == "__main__":
    build_knowledge_base()
