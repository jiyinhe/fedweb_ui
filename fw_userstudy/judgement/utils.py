import re
import urllib
reg_img = re.compile('"http://.+?"')
reg_tag = re.compile('<.+?>', re.MULTILINE|re.DOTALL)
def clean_snippet(s):
	tags = reg_tag.findall(s)	
	for t in tags:
		#Only keep images that are available
		rmv = 1
		if t.startswith('<img') and 'http' in t:
			img = reg_img.findall(t)	
			if len(img)>0:
				url = img[0].replace('"', '')
				if urllib.urlopen(url).getcode() == 200:
					rmv = 0	
					s = s.replace(t, '<br/>%s<br/>'%t)
		if rmv == 1:
			s = s.replace(t, ' ')
	return s
			
def clean_html(html):
#	f = open('tmp', 'w')
#	f.write(html)
#	f.close()
	# Only keep body part
	reg_body = re.compile('<body.*?>.+?</body>', re.MULTILINE|re.DOTALL)
	body = reg_body.findall(html)
	if body == []:
		text = html
	else:
		text = body[0] 	
	# clean javascriptsscripts
	reg_s = re.compile('<script.*?>.+?</script>', re.MULTILINE|re.DOTALL)
	text = reg_s.sub('', text)

	# clean inputs 
	reg_f = re.compile('<input.+?>')
	text = reg_f.sub('', text)
	reg_b = re.compile('<button.*?>.*?</button>')
	text = reg_b.sub('', text)
	reg_t = re.compile('<textarea.*?>*?</textarea>')
	text = reg_t.sub('', text)
	text = re.sub(r'<form .+?>', '', text)
	text = re.sub('</form>', '', text)

	#clean class style
	reg_c = re.compile('class=".+?"') 
	text = reg_c.sub('', text)
	
	# disable links 
	text_clean = re.sub(r'href=".+?"', '', text)

	# disable images if it's a relative path
	reg_img = re.compile('<img.*?/*>', re.MULTILINE|re.DOTALL)
	reg_src = re.compile('src=".+?"')	
	imgs = reg_img.findall(text_clean)
	for img in imgs:
		src = reg_src.findall(img)
		if len(src)>0:
			if not src[0].split('"')[1].startswith('http'):
				text_clean = text_clean.replace(img, '')
	# clean empty lists
	text_clean = re.sub(r'<li.*?></li>', '', text_clean)
	# remove 'body' tag
	text_final =  re.sub(r'<.*?body.*?>', '', text_clean)

	if text_final.strip() == '':
		text_final =  'Sorry, the content of the document is not available.'

	return text_final
