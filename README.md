# Usage
`json2graphml.py` : reads pipe API from a Sesam subscription and creates a node-edge graph from systems and pipes.

Env.vars:
- `BASE_URL` : Base URL to the Sesam subscription (ex: `https://datahub-abcd1234.sesam.cloud`)
- `JWT` : JWT to access the Sesam subscription

Output: `graph.graphml`

`graphml2yEd.py` : transforms graphml to yEd readable graphml XML.

Input: `graph.graphml`

Output: `graph.yed.graphml`
