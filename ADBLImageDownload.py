#!/usr/bin/python

import requests
import json

def main():
    data = json.loads(open('adbl.data').read())

    print '{} Items found'.format(len(data))

    for i,x in enumerate(data):
        print str(i),':',
        if 'img' not in x: 
            print 'Item has no image link'
            continue

        img=x['img']
        filename=img.split('/')[-1]

        req=requests.get(img, stream=True)

        if req.status_code == 200:
            chn=0
            with open('img_cache/'+filename,'wb') as f:
                for ch in req.iter_content(1024):
                    f.write(ch)
                    chn+=1
                print 'Succesfully downloaded {} ({} chunks)'.format(filename,chn)
        else:
            print 'Bad request ({})'.format(req.status_code)

if __name__=='__main__': 
    main()
