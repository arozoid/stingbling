import os
import re

def slugify(text):
    # Special cases for slugs to match References.md
    slug_map = {
        "Spotted jelly": "spotted-jelly",
        "Australian box jellyfish": "australian-box-jellyfish",
        "Tomato jellyfish": "tomato-jellyfish",
        "Moon jelly": "moon-jelly",
        "Marble jelly": "marble-jelly",
        "Sand jellyfish": "sand-jellyfish",
        "Sea wasp": "sea-wasp",
        "Amakusa jelly": "amakusa-jelly",
        "Edible jellyfish": "edible-jellyfish",
        "Philippine Irukandji": "philippine-irukandji",
        "Sivickis’ Box jelly": "sivickis-box-jelly",
        "Alarm jellyfish": "alarm-jellyfish",
        "Ghost jellyfish": "ghost-jellyfish"
    }
    if text in slug_map:
        return slug_map[text]
    
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def parse_references(ref_file):
    if not os.path.exists(ref_file):
        return {}
    with open(ref_file, 'r') as f:
        content = f.read()
    
    references = {}
    sections = re.split(r'##\s+', content)
    for section in sections[1:]:
        lines = section.strip().split('\n')
        if not lines:
            continue
        slug = lines[0].strip()
        refs = []
        for line in lines[1:]:
            match = re.match(r'\d+\.\s+(.*)', line)
            if match:
                refs.append(match.group(1))
        references[slug] = refs
    return references

def clean_text(text):
    # Remove HTML tags like <span>
    text = re.sub(r'<span.*?>|<\/span>', '', text)
    # Remove excessive stars/formatting from the text part
    text = text.replace('**', '').replace('*', '').strip()
    return text

def parse_output(output_file):
    with open(output_file, 'r') as f:
        content = f.read()
    
    # Split by headers
    sections = re.split(r'###\s+', content)
    jellyfish_data = []
    
    for section in sections:
        lines = section.split('\n')
        if not lines:
            continue
        
        name = lines[0].strip()
        if name == "Template" or name == "Name" or not name:
            continue
            
        body = '\n'.join(lines[1:]).strip()
        
        # Extract scientific name for frontmatter
        sci_match = re.search(r'\*\*Scientific name\*\*(.*?):\s*(.*)', body, re.IGNORECASE)
        scientific_name = ""
        if sci_match:
            scientific_name = clean_text(sci_match.group(2).split('\n')[0])

        # Extract threat level for frontmatter
        threat_match = re.search(r'\*\*Threat\*\*(.*?):\s*(.*)', body, re.IGNORECASE)
        threat_level = ""
        if threat_match:
            threat_level = clean_text(threat_match.group(2).split('\n')[0])

        # Extract image
        image_match = re.search(r'!\[.*?\]\(Images/(.*?)\)', body)
        hero_image = ""
        if image_match:
            hero_image = f"/images/jellyfish/{image_match.group(1)}"

        # Clean body for content
        # Replace ^[n]^ and ^[n}^ with [^n]
        cleaned_body = re.sub(r'\^\[(\d+)\]\^', r'[^\1]', body)
        cleaned_body = re.sub(r'\^\[(\d+)\}^', r'[^\1]', cleaned_body)
        
        # Standardize headers in body
        def fix_label(m, label):
            content = m.group(2).strip()
            # Strip leading stars and punctuation from content
            content = re.sub(r'^(\*\*|\*|:|\s)+', '', content).strip()
            return f"**{label}:** {content}"

        cleaned_body = re.sub(r'\*\*Name/s\*\*(.*?):\s*(.*)', lambda m: fix_label(m, "Name"), cleaned_body, flags=re.IGNORECASE)
        cleaned_body = re.sub(r'\*\*Name\*\*(.*?):\s*(.*)', lambda m: fix_label(m, "Name"), cleaned_body, flags=re.IGNORECASE)
        
        def fix_sci_name(m):
            content = clean_text(m.group(2).split('\n')[0])
            return f"**Scientific name:** *{content}*"
        cleaned_body = re.sub(r'\*\*Scientific name\*\*(.*?):\s*(.*)', fix_sci_name, cleaned_body, flags=re.IGNORECASE)
        
        cleaned_body = re.sub(r'\*\*Class\*\*(.*?):\s*(.*)', lambda m: fix_label(m, "Class"), cleaned_body, flags=re.IGNORECASE)
        cleaned_body = re.sub(r'\*\*Description\*\*(.*?):\s*(.*)', lambda m: fix_label(m, "Description"), cleaned_body, flags=re.IGNORECASE)
        cleaned_body = re.sub(r'\*\*Habitat\*\*(.*?):\s*(.*)', lambda m: fix_label(m, "Habitat"), cleaned_body, flags=re.IGNORECASE)
        cleaned_body = re.sub(r'\*\*Threat\*\*(.*?):\s*(.*)', lambda m: fix_label(m, "Threat"), cleaned_body, flags=re.IGNORECASE)
        cleaned_body = re.sub(r'\*\*Fun fact\*\*(.*?):\s*(.*)', lambda m: fix_label(m, "Fun fact"), cleaned_body, flags=re.IGNORECASE)
        cleaned_body = re.sub(r'(\*\*Fun fact\s*:)\s*(.*)', lambda m: fix_label(m, "Fun fact"), cleaned_body, flags=re.IGNORECASE)
        
        # Replace Images/ with /images/jellyfish/
        cleaned_body = re.sub(r'\(Images/(.*?)\)', r'(/images/jellyfish/\1)', cleaned_body)

        jellyfish_data.append({
            "name": name,
            "scientific_name": scientific_name,
            "threat_level": threat_level,
            "hero_image": hero_image,
            "body": cleaned_body
        })
    
    return jellyfish_data

def main():
    base_dir = "/home/arki05/Documents/stingbling"
    output_file = os.path.join(base_dir, "stingblingprovidedmd/Output.md")
    ref_file = os.path.join(base_dir, "stingblingprovidedmd/References.md")
    content_dir = os.path.join(base_dir, "src/content/blog")
    
    if not os.path.exists(content_dir):
        os.makedirs(content_dir)
    
    references = parse_references(ref_file)
    jellyfish_list = parse_output(output_file)
    
    for jelly in jellyfish_list:
        slug = slugify(jelly["name"])
        
        # Get references
        jelly_refs = references.get(slug, [])
        
        # Construct content
        content = "---\n"
        content += f"title: \"{jelly['name']}\"\n"
        if jelly["scientific_name"]:
            content += f"scientificName: \"{jelly['scientific_name']}\"\n"
        content += f"date: \"2026-04-13\"\n"
        
        sci_part = f"{jelly['scientific_name']} – " if jelly['scientific_name'] else ""
        excerpt = f"{sci_part}Found in Palawan. Threat level: {jelly['threat_level']}"
        content += f"excerpt: \"{excerpt}\"\n"
        
        if jelly["hero_image"]:
            content += f"image: \"{jelly['hero_image']}\"\n"
        content += "category: \"Jellyfish Guide\"\n"
        if jelly["threat_level"]:
            content += f"threatLevel: \"{jelly['threat_level']}\"\n"
        content += "---\n\n"
        
        content += jelly["body"]
        
        if jelly_refs:
            content += "\n\n---\n\n**References**\n\n"
            for i, ref in enumerate(jelly_refs, 1):
                content += f"[^{i}]: {ref}\n"
        
        # Write to file
        file_path = os.path.join(content_dir, f"{slug}.md")
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Generated {file_path}")

if __name__ == "__main__":
    main()
