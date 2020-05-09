# Liteblue

## Rpc and beyond...

Every time I start a project by making its model - I forget - I think to myself:

> I could auto-generate the interface;
> it can't be that difficult, after all -
> I have all the types and relations defined in sql!

Then I wake up and remember that I serve up graphs - views to the client and that crud is an illusion. Rest encourages crud. GraphQL encourages I don't know what - but it sure generates a lot of code. GraphiQL is amazing! But I want to go a step easier...

This is a function I'd like to make available to the client:

```python
__all__ = ["add"]

def add(a:int, b:int) -> int:
    ''' simple addition of a to b '''
    return a + b
```

I have annotated the parameters and return types. I added documentation. In order to make it available to outside users - outside of the module - I add it to the modules `__all__` property.

To call from inside a Vuex Store action I could write:

```javascript
this.$rpc.call("add", {a:2, b:2}).then(
    response=>{
        console.log(response);
        return response;
    },
    error => {
        commit("set_error", error)
        return error;
    })
```

Liteblue uses Websockets, but it can use Ajax and EventSource instead. When you change the server's state all the clients should know about it. The obvious example is a chat room:

```python
from liteblue import context

__all__ = ['say']

def say(what: str) -> None:
    ''' broadcasts what to other clients '''
    email = context.current_user()["email"]
    message = f"{email} says: {what!r}"
    context.broadcast({"mutation": "said", "message": message})
```

And the Vuex Store, the Websockets would call your mutation called `said`.


### Tutorial

Ok, a function and a broadcast - What about some real logic. We start with SqlAlchemy and Alembic. Actually, we start with Invoke. Invoke makes building a `command-line interfaces` a sinch. Liteblue has a couple of tasks to make creating an app easier.

```bash
(venv)% liteblue -l
subcommands:

    create      creates a new project with a sqlite db
    downgrade   downgrades db to base or revision
    revise      creates an alembic database revision
    run         run a liteblue project
    upgrade     upgrades db to head or revision
```

Lets build a liteblue project called Calc, from scratch:
```bash
% python3 -m venv venv
% . venv/bin/activate
(venv) % pip install liteblue
(venv) % liteblue create calc
(venv) % liteblue run calc
```

Now head over to http://localhost:8080 and see the functions that you can call...

Welcome back. Take a moment to have a look at the generated project. You'll notice that a Dockerfile has been created and a docker-compose.yml. These allow you to bundle you app as a container. Also, an alembic script folder has been added to the calc package that can be amended via the db invoke tasks: upgrade, downgrade and revise.

Liteblue is written atop [Tornado](https://www.tornadoweb.org) and uses [Redis](https://redis.io) to scale broadcasting. You can also run headless tornados as workers that a queued via redis. But the ease with which you can add functionality and offer realtime data with transactions - this is what an rpc can offer.

So what is happening under the hood. If we change our add function to be asynchronous what then:

```python
__all__ = ["add"]

async def add(a:int, b:int) -> int:
    ''' simple addition of a to b '''
    return a + b
```

Nothing - no change. Liteblue executes synchronous functions in a ThreadPoolExecutor and Async functions become asyncio tasks. To perform function inside the queue you can call thread-safe `perform` in the `liteblue.context`.

The context also contains a function `current_user` which is populated in context.local or thread.local depending on which type of function you are in. It also contains `broadcast` which gives you access to all connected clients. If you have multiple servers the broadcast goes through redis.
