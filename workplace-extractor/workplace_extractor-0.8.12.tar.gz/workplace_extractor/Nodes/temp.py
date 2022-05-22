import json

sum1 = 0
sum2 = 0

for i in range(1, 2):
    print(f'json{i}.json')
    with open(f'output/json{i}.json') as json_file:
        data = json.load(json_file)

        for p in data['data']:
            if not p.get('parent', {}):
                sum1 += p.get('reactions', {}).get('summary', {}).get('total_count', 0)
            else:
                sum2 += p.get('reactions', {}).get('summary', {}).get('total_count', 0)


print(f'comments reactions = {sum1}')
print(f'replies reactions = {sum2}')

# with open('nodes.pickle', 'wb') as handle:
#    pickle.dump(self.nodes, handle)
# with open('nodes.pickle', 'rb') as handle:
#    self.nodes = pickle.load(handle)



"""

    async def fetch_posts_info(self):
        http_calls = {}
        for node in self.nodes.nodes:
            for post in node.feed.nodes:

                http_calls[f'seen_{post.node_id}'] = {
                    'url': f'{self.extractor.url_GRAPH}/{post.node_id}/seen?fields=id&limit=100&summary=1',
                    'call': self.call_views if self.extractor.export == 'INTERACTIONS' else self.call_count,
                    'post': post,
                    'type': 'seen'}

                http_calls[f'reactions_{post.node_id}'] = {
                    'url': f'{self.extractor.url_GRAPH}/{post.node_id}/reactions?fields=id,type&limit=100'
                           f'&summary=1',
                    'call': self.call_reactions if self.extractor.export == 'INTERACTIONS' else self.call_count,
                    'post': post,
                    'type': 'reactions'}

                http_calls[f'comments_{post.node_id}'] = {
                    'url': f'{self.extractor.url_GRAPH}/{post.node_id}' + '/comments/stream?fields=id,from,'
                                                                          'parent{id}&limit=100&summary=1',
                    'call': self.call_comments if self.extractor.export == 'INTERACTIONS' else self.call_count,
                    'post': post,
                    'type': 'comments'}

                author = next((node for node in self.nodes.nodes if node.node_id == post.author_id), None)

                # including Bots
                if author is not None:
                    author = copy(author)
                    author.feed = None

                    post.author = author
                else:
                    bot = []
                    http_calls[f'bot_{post.node_id}'] = {
                        'url': f'{self.extractor.url_GRAPH}/{post.author_id}',
                        'call': self.call_bot,
                        'author': bot,
                        'post': post}

        await self.extractor.fetch(http_calls)
        

    async def call_views(self, url, session, **kwargs):

        data = await self.extractor.fetch_url(url, session, 'Interaction')

        if 'data' in data and data['data']:
            for item in data['data']:
                view = View()
                self.set_author(item, view, kwargs.get('type'))

                kwargs.get('post').views.append(view)

            if 'paging' in data and 'next' in data['paging']:
                await self.call_views(data['paging']['next'], session, **kwargs)

    async def call_reactions(self, url, session, **kwargs):
        data = await self.extractor.fetch_url(url, session, 'Interaction')

        if 'data' in data and data['data']:
            for item in data['data']:
                reaction = Reaction(item)
                self.set_author(item, reaction, kwargs.get('type'))

                kwargs.get('post').reactions.append(reaction)

            if 'paging' in data and 'next' in data['paging']:
                await self.call_reactions(data['paging']['next'], session, **kwargs)

    async def call_comments(self, url, session, **kwargs):
        data = await self.extractor.fetch_url(url, session, 'Interaction')

        if 'data' in data and data['data']:
            for item in data['data']:
                comment = Comment(item)

                self.set_author(item, comment, kwargs.get('type'))

                url_reactions = f'{self.extractor.url_GRAPH}/{comment.node_id}/reactions?fields=id,type&limit=100'
                kwargs_reaction = {'post': comment, 'type': 'reactions'}
                await self.call_reactions(url_reactions, session, **kwargs_reaction)

                if 'parent' in item:
                    parent = next((node for node in kwargs.get('post').comments.nodes if
                                   node.node_id == item.get('parent', {}).get('id')), None)
                    if parent is not None:
                        parent.comments.extend(comment)
                else:
                    kwargs.get('post').comments.extend(comment)

            if 'paging' in data and 'next' in data['paging']:
                await self.call_comments(data['paging']['next'], session, **kwargs)

    async def call_views2(self, url, session, **kwargs):

        data = await self.extractor.fetch_url(url, session, 'Interaction')

        if 'data' in data and data['data']:
            for item in data['data']:
                view = View()
                self.set_author(item, view, kwargs.get('type'))

                kwargs.get('post').views.append(view)

            if 'paging' in data and 'next' in data['paging']:
                await self.call_views(data['paging']['next'], session, **kwargs)

    async def call_reactions2(self, url, session, **kwargs):
        data = await self.extractor.fetch_url(url, session, 'Interaction')

        await self.call_info_reactions(data, session, **kwargs)

    async def call_comments2(self, url, session, **kwargs):
        data = await self.extractor.fetch_url(url, session, 'Interaction')

        if 'data' in data and data['data']:
            for item in data['data']:
                comment = Comment(item)

                self.set_author(item, comment, kwargs.get('type'))

                url_reactions = f'{self.extractor.url_GRAPH}/{comment.node_id}/reactions?fields=id,type&limit=100'
                kwargs_reaction = {'post': comment, 'type': 'reactions'}
                await self.call_reactions(url_reactions, session, **kwargs_reaction)

                if 'parent' in item:
                    parent = next((node for node in kwargs.get('post').comments.nodes if
                                   node.node_id == item.get('parent', {}).get('id')), None)
                    if parent is not None:
                        parent.comments.extend(comment)
                else:
                    kwargs.get('post').comments.extend(comment)

            if 'paging' in data and 'next' in data['paging']:
                await self.call_comments(data['paging']['next'], session, **kwargs)





            elif type == 'Summary':
                response = await resp.json(content_type='application/json')
                if 'summary' not in response:
                    return Summary({'total_count': 0})

                return Summary(response['summary'])

            elif type == 'Interaction':
                response = await resp.json(content_type='application/json')
                return response
                
            elif type == 'GRAPH':
                response = await resp.json(content_type='application/json')
                return response['data']
        
"""


import pickle

with open('output/workplace_interactions.pickle', 'rb') as handle:
    nodes = pickle.load(handle)



comments = 0
replies = 0
for node in nodes.nodes:
    for post in node.feed.nodes:
        comments += len(post.comments['data'].nodes)
        for comment in post.comments['data'].nodes:
            replies += len(comment.comments.nodes)

print(comments)
print(replies)

