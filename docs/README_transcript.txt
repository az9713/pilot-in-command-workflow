https://www.youtube.com/watch?v=Y3Vb6ecvfpU&t=19s

NVIDIA releasing their best models as open weights isn't charity — it's a business decision. And honestly, it's one of the clearest explanations I've heard for why a company would invest heavily in open AI.

I sat down with Bryan Catanzaro, VP of Applied Deep Learning Research at ‪@NVIDIA‬, to talk about the Nemotron-3 rollout and what's really going on inside NVIDIA's AI org. Bryan's been at NVIDIA since the early CUDA days (he literally coined the name "Megatron"), left to work at Baidu's AI Lab with Andrew Ng and Dario Amodei, and came back to build NVIDIA's applied research group.

Transcript & links: https://www.interconnects.ai/p/why-nv...

We cover...

00:00:00 Intro & Why NVIDIA Releases Open Models
00:05:17 Nemotron's two jobs: systems R&D + ecosystem support
00:15:23 Releasing datasets, not just models
00:22:25 Organizing 500+ people with "invitation, not control"
0:37:29 Scaling Nemotron & The Evolution of Megatron
00:48:26 Career Reflections: From SVMs to DLSS
00:54:12 Lessons from the Baidu Silicon Valley AI Lab
00:57:25 Building an Applied Research Lab with Jensen Huang 
01:00:44 Advice for Researchers & Predictions for 2026

Transcript


0:06
Okay. Hey Brian, I'm very excited to talk about Neatron. I think low-key one
0:12
of the biggest evolving stories in 2025 of open models outside the obvious things in China that everybody talks
0:18
about that gets a ton of attention. So, thanks for coming on the pod. Oh, yeah. It's my honor.
0:24
So, I wanted to start. Some of these questions are honestly fulfilling my curiosity as a fan as like why does
0:31
Nvidia in a basic level release Neatron as open models?
0:39
Well, we know that um it's an
0:45
opportunity for NVIDIA to grow our market whenever AI grows. And we know that um uh having access to open AI
0:54
models is really important for a lot of developers and researchers that are trying to push AI forward. Um you know
1:02
we were really excited uh by efforts from some other companies around the
1:07
industry to push um openly developed AI forward. you know, Meta did um some
1:13
amazing work obviously with Llama and um you know, OpenAI released GPTOSS which
1:19
was exciting and the Allen Institute of course has been you know really uh leading the charge um u for research
1:26
open open research and you know also things like um the Marin project um uh
1:32
and open Athena you know like there's there's a bunch of things that um we're always excited to see develop and you
1:40
know As we think about where AI is going to go, you know, Nvidia believes that AI
1:46
is a form of infrastructure. Um it's AI is a very useful technology when it's
1:52
applied, but on its own um you know, it's kind of a foundation um infrastructure. We think that um
2:00
technology generally works better when there's openness to the infrastructure so that people can build things in
2:06
different ways. You know, you think about um the way that the internet transformed every aspect of the world
2:12
economy um is pretty profound and we're not done yet. But the way that for
2:17
example, retail uses the internet is different from the way that healthcare uses the internet. and the fact that um
2:23
you know different sectors of the economy were able to figure out how to incorporate the internet into the
2:29
beating heart of their businesses in different ways was possible because the internet was built on open technologies
2:35
that you know allowed people to try different things and um we think AI is going to um evolve in a similar way that
2:43
organizations across um every sector of the world economy are going to find new and surprising and fun and important
2:49
things to do with AI and they'll be able to do that better if they have the
2:55
ability to customize uh AI and incorporate it directly uh into the work
3:00
that they do. Uh and so um and by the way, this is not to detract from any of
3:06
the um you know, more closed approaches to AI, you know, the APIs that that we
3:11
see from a number of leading labs that, you know, are just extraordinary and have amazing capabilities. We're excited
3:17
about those, too. you know, Nvidia um uh loves to support AI in in all of its
3:22
manifestations, but we we feel like right now um the sort of closed
3:27
approaches to to deploying AI are doing pretty well. Uh but we, you know, could
3:34
use some more energy in the openly developed AI ecosystem. And so, um that's why we've been putting more
3:40
effort into it this past year. Yeah. So, I'm definitely going to dig into this a lot because I have seen
3:46
this. We're sitting here recording in January 2026, which is in the midst of the roll out of these Neatron 3 models.
3:51
There's the I think the Nano has released in the fall, which was probably one of the biggest splashes that ORC has
3:57
made and everybody's eagerly awaiting these super and ultra larger variants and it's like
4:04
how far you how far are you willing to push this Neatron platform? Like is it
4:09
just depending on the users and the uptake and the ecosystem? like like what is the is there a north star in this
4:15
where you hear a lot of if you listen to a lot of other open labs they're like we want to build open AGI which is like I
4:21
don't necessarily think grounded but there's like a very unifying vision is there something that you try to set the
4:28
tone for it that goes through the organization I mean AI2 it's like you know my academics is
4:33
for Neotron yeah go ahead oh sorry go ahead
4:39
I was just going to compare to like AI2 where we can have such a like we have a very specific vision being so open that
4:45
it's like I think like research is so needed and there's so little recipes to
4:50
build on like with really credible research. So this is like a research infrastructure and then when you have
4:56
something like Llama it was like built on Zuckerberg's vision and he changed
5:02
his mind which I actually thought his vision was was excellent the way he articulated the need for open models and
5:07
it it kind of faded. So it's like is there a way to set a vision for an org that like permeates every everyone and
5:15
is really compelling and exciting, right? Well, we build Neotron for two
5:20
main reasons. The first is because uh we need to for our uh main product line. So
5:27
what do I mean by that? Well, accelerated computing what Nvidia does, we we build fast computers, right? But
5:33
the point of building fast computers is to help people do new things. Um, and actually, uh, every fast computer is
5:41
also a slow computer. Um, you know, the observation that it would be nice if
5:46
computers were faster and could do more things isn't new. That's been around since the beginning of of computing. So,
5:52
what what makes accelerated computing different from standard computing is that we're prioritizing. You know, we're
5:58
focusing. We're deciding we're going to accelerate this workload, this other workload, which is like 99% of all of
6:05
the workloads. we're gonna let somebody else do that, right? So like you do not buy NVIDIA systems to do any general
6:12
purpose computation. You buy them for a purpose, right? Which is um these days all about AI. But when you think about
6:19
the workload, the compute workloads involved in AI, uh there's a there's a lot of diversity, um and there's a lot
6:26
of really important uh uh uh parameters, hyperparameters or uh algorithmic
6:32
approaches that uh all have enormous impacts on the systems that we need to
6:37
build for AI. So things like numeric precision um uh architecture which of
6:44
course influence it influences network design um you know we're dreaming about
6:49
sparity you know we've had we've had sparse neural network acceleration in the GPU since ampier um I don't think
6:56
that it's being used enough uh you know so how do we how do we figure out how to use that these these sorts of things
7:03
have an enormous impact on the future of Nvidia's main product line and we have
7:08
to understand the answers to those questions deeply ourselves in order to know what we're going to build. We can't
7:14
just go to our customers and do a survey and say, "Hey, um, you know, Meta, for
7:20
example, since we were just talking about them, what would you like to see in a future product line from Nvidia?"
7:25
Of course, Meta is always um trying to help us as much as they can, but there's limits to what they can tell us because,
7:31
you know, um a lot of the information uh that influences the design of these systems, it's very expensive to derive.
7:38
And so therefore, it's it's very closely held. And um so we need to be able to
7:44
understand uh these questions very deeply in order to understand what kinds of systems to build, in order to
7:50
understand what we're accelerating in AI and what we're uh not going to worry about. Uh, and so that's kind of the
7:56
first job for Neotron models is to make it possible for Nvidia to continue to exist as a company. And I think it's
8:04
important that the community knows that because um that's the reason why Nvidia
8:10
is making the investments in Neotron is because we believe it's essential for the future of our company. Um, and so
8:18
this isn't although as much as much as it feels good to to say, you know, Nvidia believes in open uh openly
8:25
developed AI because um uh you know, we're so charitable.
8:30
But actually that's not the case. This is actually a business decision like for NVIDIA. our business needs us to know
8:39
about AI very deeply and um and and so you know the amount of investment that
8:46
um is justified to carry on Nvidia's ongoing business I think is large um and
8:51
so that's um that's job number one for Neotron now um job number two for Neotron is to support the ecosystem more
9:00
broadly outside of Nvidia um and you know Nvidia has a special position in uh
9:06
the AI landscape. Um of all of the big AI companies, uh I think we're the one
9:11
that works um with the most other companies. We support every company um
9:17
small and large AI native company to old um established enterprise. We work with
9:23
hyperscalers. We work with tiny little startups. We work with um countries around the world.
9:29
Um so we have this unique uh position and and I think also unique
9:35
responsibility and al maybe also a unique opportunity that whenever AI is
9:40
able to grow uh in any sort of direction in any um capability then uh you know
9:47
that's an opportunity for us to grow our business. Obviously, it's not automatic, right? Um, uh, you know, the AI market
9:54
is diverse and it's getting more diverse and it should be because it's the most important market in the history of humanity. So, um, uh, so we we
10:02
acknowledge that and at the same time, we know that it's in our interest to develop, uh, the AI ecosystem. The more
10:09
people that are building, inventing, and deploying AI, the more opportunity that we have as a company. So, that's job
10:15
number two for Neotron. Yeah, I really appreciate you saying it so directly because it's like we've worked we I
10:21
launched this thing the atom project last summer which is trying to get more investment in us open models and I was like the only company that has an
10:28
obvious business model for open models is something like Nvidia where you need to make sure that the open models and
10:34
the research ecosystem plays nicely on CUDA because then you're going to be able to be one you're so many steps
10:39
closer to research that's happening if not like if like there's such an advantage to have research happen mostly
10:45
on GPUs relative to AMD or anything like this. So, well, you know, we we are we're we're
10:51
not thinking about how to prevent competition. You know, we welcome competition. There's lots of
10:56
competition. There should be more competition in this space, but um but we are um very self-interested in staying
11:03
engaged with the community. You know, it's very important. you know, CUDA, not many people remember this because it
11:10
happened so long ago, but um you know, CUDA started out with a lot of outreach from Nvidia to the academic uh and and
11:19
industrial community saying, "Hey, we have this new way of doing computing. Um we'd love to see what you can do with
11:24
it." In fact, you know, I started uh using CUDA in 2006 uh when I was a grad
11:30
student at Berkeley um because uh David Kirk, who was the chief scientist of
11:35
NVIDIA at the time, came over to Berkeley and said, "Hey, uh we just released this new GPU and it has this
11:40
new programming uh model called CUDA. You should give it a try." And I um I
11:46
was at the time I was working on machine learning on FPGAAS. And I um I had been
11:51
working on this one particular piece of uh of support vector machine training on the FPGA and I I decided to take that
11:58
little piece and and write it in CUDA and it took me like 15 minutes and then I ran it and it was like 200 times
12:04
faster than my single threaded CPU code and I was like whoa that was way easier than what I was doing before. I'm just
12:10
going to go do that. Right? So like my own personal involvement with um CUDA
12:15
and NVIDIA came about because of this outreach that Nvidia conducted right from the beginning of CUDA. Um you know
12:22
of course that led to a lot of great things for NVIDIA including AlexNet which was another academic project you
12:28
know where um Alex Kessevki and Ilaskcover were um thinking about how do we train larger neural networks on more
12:35
data. uh we're going to go write a bunch of GPU code that uses the GPU in a in a kind of new and clever way so that we
12:42
can train a better image classification model. And you know that um had such astonishing results it kicked off the
12:48
deep learning era for the whole community. Um and again not something that could have been done uh top down.
12:55
that was a that was a very much a um a result of uh Nvidia supporting open
13:01
development and re research uh uh in parallel computing and and artificial intelligence. And so we remember that
13:08
and we're thinking about uh in 2026 what does it look like to help you know the
13:13
um Alex Kvski uh of the future who's who's a grad student in a lab somewhere
13:19
invent the next technology that changes the world. it seems really difficult to do that without um something like uh
13:25
Neotron or or or the other openly developed AI projects out there. Um yeah, I I also want to say um uh in
13:33
regards to this uh Neotron is not trying to be the only project out there. We're
13:39
part of the community. We love other people doing great work in openly developed AI. We learn from things that
13:46
other people do. uh and um you know so we're we're trying to support the community because it's in our interest
13:52
but we uh you know we we're very happy to see other people contributing as well. Yeah. I mean I can transition to
13:59
something I wanted to ask about is like I see multiple ways 2025 Neimatron m
14:06
I I don't want to use the word maturing because I want to ask you about how it feels in the org but just like the output reached levels that were more
14:13
noticed by the community and people building with models. And there's a lot of ways that that can happen, but one of them is like in my niche community, I've
14:19
been using Neimatron data sets a lot. Like we when we redo our post- training recipe, one of the only people we look
14:25
at is like, okay, Nvidia, Nevatron has released a lot of high quality, openly licensed um post- training data. Um this
14:31
year, you also started releasing some pre-training data, which among AIT got a lot of notice. Like what is that? Is
14:39
that like a distinct shift within Neatron? Is that something that you've wanted to do for a while and finally
14:45
just did? But it's because it's like it is just like a zero to one moment where releasing pre-training data comes with
14:51
legal risk for any company. But so few people do it where on my side of the
14:57
world it's like pretty easy to normally say what the best pre-training data set is. And it had for a long time
15:02
oscillated between like hugging face AI2 DCLM and there was like literally only two or three options. So in terms of
15:09
fundamental research, like I think that's a big step from an org to support the community and take on some risk. So
15:16
if you have any story you can tell and or just say like I appreciate it. That's that's all that's all I got.
15:23
Well, yeah. I mean, so I think it'd be great if more people could understand that Neotron is uh not just a model,
15:31
right? Like what we're trying to do with Neatron is to support openly developed AI because again that's our big
15:39
opportunity right now. There's a lot of organizations that are incentivized to build a model and the model is maybe the
15:46
thing that um runs their business right but at NVIDIA the the model is not the thing that runs our business. It's the
15:52
systems. So um when we're thinking about how do we support the ecosystem it's
15:57
clear to us that the ecosystem needs more than just a model. There's a lot of models out there already, you know, and
16:03
of course we want Neotron to be awesome, but um you know, if Neotron can convince
16:09
um other people to work on AI because of a data set or a technique, you know, we're we're trying to be very open with
16:16
all of the things we learn, you know, including I mean, we do a lot of expensive experiments in order to figure
16:21
out how to do blending for our data sets or to figure out, you know, optimizer settings and, you know, these these
16:27
sorts of things. um we're very happy for other people to pick that up and run with it if it's
16:33
useful to them, you know, and um so that makes Neotron a different kind of AI
16:40
effort. Of course, there is a model component and that's a tangible thing and it's it's easy to focus on that, but
16:46
we see Neotron as as um you know, an effort that includes models, but also includes data sets, techniques, all of
16:53
um all of the research that goes into Neotron. And again, um, we're a unique
16:59
kind of AI organization because of the way that we work with, um, AI companies
17:05
around the industry and because of the way that our business works, we can afford to be more open, uh, with some of
17:11
these things than than maybe some other organizations could be. Now, um, to your question about like does it take some
17:18
uh, courage uh, in order to be open? Yeah, absolutely it does. Um and uh you
17:25
know I think there's been one of the things that's happened in 2025 is that there's been an evolving understanding
17:31
within Nvidia about the benefits of openness and that has really enabled the
17:37
company to make some investments that perhaps it was um a little gunshy to make in the past and um so that's really
17:45
encouraging for me. uh is something that I've um you know advocated for for a while and so it's it's great to see um
17:52
the company kind of lining up behind it. Um I also you know to your point about like 2025 being a a year where where
18:00
Neotron really made some strides. I want to um uh say thank you for noticing that
18:06
and then maybe tell you a little bit about how that happened because I think it's um instructive for me about how I
18:13
think the work is going to go forward uh in the future. So um you know Nvidia is
18:19
a a very decentralized uh company with a lot of volunteers. You know everybody
18:24
that works at Nvidia is a volunteer. And what do I mean by that? Well I mean look the industry is um moving quick. you
18:31
know, people can always move from one one job to the next. So, um the way that we think about the work that we do is
18:37
like it's very decentralized. It's very much um let smart people figure out um
18:43
what they should be doing and then kind of self-organize. Now, um, one of the challenges of self-organization in a
18:50
field that's moving quickly is that sometimes, um, a whole bunch of people decide to, uh, do uh, similar kind of
18:58
overlapping things, but aren't really coordinated. Um, and that's okay at the beginning because, you know, uh, in a
19:04
place like Nvidia, it's just great to to have some energy. It it took us a while I think as a company to figure out that
19:12
uh Neimotron was better together that rather than having like this group has a
19:17
has a model and that group has a data set and like you know then we end up publishing papers that kind of um you
19:23
know don't really acknowledge each other and aren't really coordinated and then of course uh along with that we need to
19:30
have K times the GPUs where K is the number of independent efforts. Um, we
19:36
realized that, you know, um, building AI, you really do need to to figure out
19:41
how to collaborate. Um, the, um, the AI efforts that are built from teams of
19:48
people focused on the overall effort succeeding rather than their own particular piece of the project
19:54
succeeding. Those are the ones that, you know, really change the world. And, you know, of course, Nvidia works that way
19:59
for the systems that we build, right? So like the people working on the memory controller on the GPU know that they
20:06
also have to work with the people working on the SM that does the the math, right? Like you can't you can't
20:11
make a GPU where where it's just like well we've got an awesome memory controller if the math doesn't work, right? It all has to has to kind of work
20:18
together. And so um that coordination I think in the field of AI it took us a
20:25
little bit longer um to do maybe than uh uh you could imagine that it could have
20:31
uh and I think that slowed the progress for Neotron. Um, so I give a lot of
20:36
credit to the Neotron team for realizing over the past, I don't know, year and a half or so that um, it was really time
20:43
to to join up and build one thing and make it awesome and and deeply
20:48
understand that the success of the Neotron project was more important than uh, the success of any individual piece
20:55
of that project. And um, the reason why I'm telling you all of this is because I
21:00
think that's actually true more broadly than just inside Nvidia. And I think it's it's difficult um you know
21:07
researchers like those of us with PhDs for example we are taught how to be independent you know and how to how to
21:14
build up our Google Scholar profile and there's like an incentive to to go ahead and and focus on that and a lot of
21:20
successful academics and and people uh researchers um you know they they
21:25
managed to push that pretty far and get some pretty amazing results. you know, I do believe that in in 2020, in the
21:31
2020s, um, you know, that, uh, the best research is done as part of a larger
21:37
team. Uh, so how do we figure out how to work together? You know, how do we figure out how to put the the success of
21:44
the team uh, first? That is a thing that is challenging to do, but um, if we can
21:50
achieve it, I think yields significant results. And you know to the extent that we made progress in that part of the
21:57
organization I think we also saw progress in the technology. Um and that's um that gives me great hope for
22:04
2026 for Neotron because um the way the team is working together I think is um
22:10
you know pretty extraordinary. There's just an enormous number of brilliant people that um uh have decided that
22:16
they're going to volunteer to make Neotron awesome. And um we're we're starting to see some some pretty great
22:22
things come together. I agree with everything you said. Do you have any advice for making that works
22:28
come together? I think we've seen big I see two class there's two classes of AI
22:33
companies right now. One is startup does everything and you have a model in six months but you're building from zero and
22:38
you have you everybody agrees when they start that they do this and then you have Google's famous long winded reorgs
22:44
which they actually eventually got right like they got it very right with what's going on with Gemini and Google de mind
22:50
right now and it's like do you have any advice on doing this I think like I'm too also advocating for this but it's
22:56
very hard I think personally it's like I mean I'm I'm a special case because I'm also visible where it's very easy for me
23:02
to turn internet activity into like reputation points because of algorithms and size, but it's very hard to do
23:10
bottomup technical work and get all of this and get all the culture alignment. So, do you have any advice on actually
23:16
like what works in this domain? You know, um what's worked for us is uh
23:24
invitation and not control. Um, so, uh,
23:29
you know, one one way that like for a while I kind of wanted to try to implement was like nobody gets to
23:36
publish any papers in AI unless they're clearly part of Neatron. So, this is
23:41
kind of a top- down like we're going to make you do it, right? Uh I came to the realization that which
23:49
we never implemented this by the way but I came to realization that this was a bad idea because it would just breed
23:54
resentment and you know Nvidia is a company of volunteers. Everybody here is a volunteer. So what we need to do is
24:00
create the conditions by which it makes sense for people to volunteer to be part of Neotron. And um uh so the way that we
24:08
went about doing that um uh first of all um it involved like some top level uh
24:15
agreements between me and um some of the other leaders of Neatron for example
24:21
John Cohen and Carrie Briskkey. Um I work very very closely with the two of them and um you know that hadn't always
24:29
been the case like we we kind of had all come to this place independently. Um but
24:34
we realized like Neimatron better together all three of us and then we started telling our teams that you know
24:40
we really think Neimatron is going to be better together. Um so that um top down
24:45
alignment I think was really helpful. Again we weren't telling people exactly what to do but we were just sending a
24:51
con um constant message like you know Neotron's better together. And then we built some structures that um
24:58
facilitated collaboration. So, uh, in the past, uh, decisions in the Neotron
25:03
project tended to be made, um, in kind of a, um, an opaque way. Um, and the
25:09
reason for that is just, you know, it's hard to tell everybody about the middle of the sausage making process. You know,
25:16
it's like messy and difficult. And so, like, you know, it's natural like researchers, we're used to to doing
25:23
this, right? It's a fata comple like here's my ICML paper and like you know the fact that you spent like two years
25:29
failing at that task before you finally succeeded and then you tied a bow around it and gave it to the ICML committee.
25:36
You don't really talk about that, right? And so it's difficult um uh for researchers to to to be open about the
25:44
middle of the process of research. There's a lot of failure and it's hard uh for people to to feel like they're
25:49
they're not not looking amazing. But what we what we decided to do is we
25:54
structured the project with um uh there's about 20 different areas
26:00
for the project. Each of them has a clear um um uh leader, what we call a
26:06
pilot in command. Their job is to the job of the pilot in command is to land the airplane. You know, you just want
26:11
the airplane to land. Okay? So, somebody if you're landing an airplane, there might be multiple pilots on board, but
26:17
only one of them is going to land the airplane at any time, right? because it would be chaos if two of them tried to
26:22
land at the same time. People would die. So um so this is not a a committee structure. It is a delineated
26:29
responsibility structure and then the the purpose of that pilot in command for each of these sections is to gather
26:35
together all the best ideas. help the group of people that are interested in working on that space to come up with
26:41
datadriven answers to what we should do, what technical decisions we should make, and then document that, you know, in a
26:48
in a way that other people can review. Um and uh you know the the thing that's
26:53
been really great about that is that um it is inviting to people because when they see like okay here's the group of
27:00
volunteers that are working on this area of uh Neotron um and then they want to
27:05
contribute it's much clearer about how they could go about doing that and it's also clearer what the group needs
27:11
because um you know these meetings are being held in the open um and we have we
27:16
actually have a website where um all of the ideas are submitted um they each get like a unique
27:22
identifier and then they get engaged with you know the pick is is um trying to understand what the implications are
27:28
what kinds of experiments need to be run in order to prove or disprove the idea how do we do what I call integration
27:34
studies you know I I integration studies are so key um for for bringing
27:40
researchers together and they're so um opposite of what we're taught when we're learning how to do ablations as a
27:46
graduate student you know rather than like isolating the um particular contribution of one idea. Integration
27:52
studies are about putting a hundred ideas together and seeing if they're better than what we had before. Um so
27:58
this kind of thing doing that um in a structured way in in a in an open way
28:03
internally um has then made it possible for more people to volunteer and that has then generally raised the rigor of
28:11
the experiments and also the I think the outcome of the work. Yeah, this is great. I think that
28:18
over the last few years there's been more consensus on things that work for research and I think that we also do
28:25
integration tests very regularly of like is this feature going to land for the model and that's kind of it's a good it's a nice mirror to ablations where we
28:35
know research is changing so much there's a lot of turmoil in the academic research community and it's nice to have
28:41
things that are tangible as ways that are a little bit different when you're doing these large scale project. So
28:46
people that like you still need to do ablations, but then it needs to survive like an additional test in order to land into
28:54
the model. So it's like an additional type of work that needs to be done. And I I just like to have words to describe
29:01
what is actually happening. [snorts] I think on the Neatron 3 nano front I do a lot
29:08
of analysis on just looking at basic adoption metrics and um Neatron we
29:14
created this what we called like a relative adoption metric which is essentially looking at downloads over time for models because it's easy to
29:20
know which models have a ton of downloads that are released a while ago but to like look at the trajectory of downloads changing over time a lot is
29:27
this a mouthful it's kind of an aside but like Neatron Nano3 was in the 30B
29:33
size range like on track to be one of the top 10 models downloaded of all time. The point that I bring this up
29:39
other than to just flatter you is like do you think last mile adoption takes a
29:44
substantial amount of work other than making like a very functional model or does adoption like do you need to like
29:50
change the recipe that you're making and put a lot of focus in evaluation and like change this over time so that you
29:56
actually get people to really use models rather than like oh the benchmarks are good look at Nvidia flying high
30:03
right yeah I mean wow it has taken and the whole company coming together in
30:10
order to make um Nano V3 um uh have more
30:15
of an impact than the models that we released before. Um and
30:21
uh there's so many different aspects to that. Uh obviously there's a lot of
30:26
technical aspects um which uh frankly I think we have more work to do. So like
30:33
um you know making sure that on day zero when we release something that the um
30:39
quantizations all the quantizations the best quantizations are out there that the speed on all of the important
30:46
inference frameworks is out there that it runs on all of the edge devices that we care about uh flawlessly that the
30:53
install experience is great. you know, this kind of work is extraordinarily
30:58
important because um you know, it's a crowded world. There's so many different things that people could choose to work
31:05
with and um any amount of friction um that gets in the way of of people even
31:10
evaluating something that you do uh is going to blunt um the results, no matter
31:15
how good that that technology is. I don't think that we're um amazing at
31:21
this yet. So this is something that I anticipate we're going to see a lot more investment in as the you know uh more
31:28
people at NVIDIA from all over the company from marketing from developer relations from software engineering you
31:35
know um uh as as they as we all come together in support of of this effort.
31:42
Um so yeah so it does it does take uh an enormous amount of work. Um and then you
31:48
know something that I'm particularly interested in is um you know how do we
31:55
work enga in a new way sort of engage with the community um to make future
32:01
neotron models even stronger. you know, um, uh, if the only things that we were
32:10
to optimize for with a Neotron model would be kind of academic benchmarks that are, you know, highly cited, um,
32:18
it's likely the case that the model wouldn't be general enough to really be useful. And so what we're trying to
32:24
build is a technology that other people can extend and deploy. And um that means
32:30
we need to have like other ways of understanding the strength of a model besides um you know a handful of of
32:36
academic benchmarks. Um I think we have a lot of room to grow here. I'm hoping
32:42
over time that we develop um the muscle of being able to engage with the
32:48
community and and learn from them like you know okay this particular thing that
32:54
I tried to do with Neotron it didn't work. it did this this other thing that you know I wasn't expecting it was
32:59
wrong. Um well that can become feedback that then is used to to make the next
33:05
version better. Um I think we've got a lot of work to do uh in that regard.
33:10
Do you think there's any magic to it? I I'm blown away by how successful open AI's too open source models are. Like
33:16
yes they're obviously the number one name brand in AI but on the same metric that I see you guys like overperforming
33:22
like what I would expect. I'm like, "Wow, like great job Nvidia." They're like totally off the charts, like on
33:27
track to like beat Llama's like most downloaded numbers ever with these two GPTO OSS models. And I feel like what
33:34
they like even on release, they had hiccups where people were pretty negative on it. But for whatever reason,
33:40
it has just like people figured it out and it just clicked and it just like for a company to say so little about it.
33:48
Like we met put so much effort into Llama being adopted and you obviously are putting a lot of effort into this
33:53
like I'm just like did OpenAI just crack the code or is there sometimes a bit of
33:58
luck? Well, I don't think uh I I I don't think about OpenAI as a as a lucky company. I
34:04
think of them as a visionary company that works incredibly hard and um you know I think their success is welld
34:10
deserved. I um I love the GPTO OSS models you know um definitely they're an
34:16
inspiration uh for us here at Neotron. Um and uh yeah, so u I think um
34:25
OpenAI also has like some um other ways of engaging with the community just
34:30
because of the large number of people that use their services and um that helps them learn things about what are
34:38
people trying to do with AI that then they can address when they're building models. And um you know obviously you
34:44
know people talk about that as a flywheel. Um, you know, I think that's um, uh, really interesting and really
34:50
important. Um, NVIDIA is never going to have the same kind of flywheel as, uh, OpenAI does. We're not trying to build a
34:58
service like chat GPT. What we're trying to do is help the ecosystem, you know,
35:03
be strong and and, uh, enduring. Uh, we think that it's important for there to be this openly developed AI ecosystem.
35:11
And also, we're we're trying to build our our next generation of systems. And so um so we have our own reasons for
35:16
doing this, but we're not ever going to have the same uh exact um uh user base or flywheel that that OpenAI does. On
35:24
the other hand, you know, we we um are able to work with um institutions around
35:29
the world in in our own way that I think um offers us different opportunities and and hopefully that um helps us make
35:35
things that are that are useful too. Yeah, this makes me realize I'm having a lot of conversations on there are many
35:42
open model efforts especially even among people that are fully open and it's like how do we better coordinate so
35:47
especially at the smaller scale it's like AI2 and hugging face so they're not big teams like how do we make sure we're not doing the same data project at the
35:53
the same exact thing at the same time and it's like I wonder if there's opportunities for open companies like LM
35:59
Marina has historically released a lot of user data to like better help us close this kind of what are people using
36:06
models for flywheel and but it's just it's very hard to build
36:12
crossorganizational model improvement pipelines is something that I think I think models become
36:17
pretty vertical in terms of somebody at Nvidia getting the feedback and the model making better so that's what would
36:24
be something I would like to see this year but I don't have ideas for doing it well yeah you know um at NVIDIA we have a
36:31
tradition of working really closely with you know organizations that use our
36:37
technology. Um uh and you know we really we have we have teams of engineers that
36:44
um their job is to enable success for our customers. Uh in fact there's more people at NVIDIA that care about the
36:51
success of people outside of Nvidia than um I feel like sometimes there are people that care about the success of
36:57
things inside Nvidia. So like sometimes I'm like I'm like hey could we use a little bit of that energy uh to support
37:04
Neotron? and and the answer is yes and Nvidia is doing that. But um uh uh I
37:10
think as Neotron matures, we're going to find that um you know the organizations
37:16
that work with Nvidia to make Neotron awesome for their business, for their use case, um are going to have a say in
37:23
how Neotron evolves. Um and hopefully that um helps uh Neotron address their needs.
37:28
Yeah, a basic question. How many people like how many employees does it take to build all the different versions of
37:35
Neatron? I haven't brought this up because you also have other great types of models. I think our like open model
37:41
analyst Florian is obsessed with the parakeet model because oh yeah much faster at typing. He's much faster at
37:47
speaking than typing. So there's a lot of other I don't know I don't have the full list of other Nvidia models off the
37:52
top of my head but you releasing a lot of varieties of models. So I think it's a bit of a um there's more context to my
37:59
original question which is I think about language models because I'm like I just think of AI's progress is going to
38:06
continue to go very fast. So I focus as that as the engine. So but it's like how many people is putting this um kind of
38:14
movement into place. Yeah. Well, it's it's it's hard to know exactly and as I said, Nvidia is a
38:20
company of volunteers, but um uh and and also these days things are changing,
38:25
right? Like so the Parakeet team, which is an excellent team by the way, um uh
38:30
they uh I I would say a year ago wouldn't have really considered themselves so much part of the core
38:37
Neotron effort, but these days they absolutely are. um for the obvious reason that you know LMS these days need
38:45
to be able to consume all sorts of data right including audio data and so um uh
38:51
you know as the pro as the characteristics the um the capabilities
38:57
of Neotron models expand uh obviously the number of people contributing is going to expand um I'd say right now um
39:06
there's about 500 people um that are working pretty much full-time time on
39:11
Neotron technologies in different ways. This is everything from numeric uh
39:17
quantization recipes to speech recognition or image understanding or
39:22
you know pre-training post- training RL systems um inference software um you
39:29
know there's there's a there's a whole bunch of different dimensions right so I'd say it's about 500 people um but
39:36
also um uh we're having our Neotron all hands meeting um uh this week and so I
39:42
took a uh to see how many people were invited um to that all hands meeting and it was about 2,000. Um so those are
39:49
people around the company that um are interested in uh working with Neotron
39:54
and and um either expanding its capabilities or helping its adoption. Um and so I think um you know the numbers
40:02
somewhere in between um and it's hopefully going to keep growing as as as Neatron matures. Yeah, I mean that's one
40:08
of the greatest attestations to what you're saying is like if the interest outside the company inside the company
40:14
is four times as big as the people doing it, you're going to you're going to keep scaling up. It seems people are going to
40:19
find ways to help. Um, one of the other things I'm interested in, I don't know, like
40:26
on the point of 500, it's like it sounds like a lot of people, but with how many things you have going on, it seems also
40:31
very few. Cuz I I'm transitioning to thinking about the long-standing like open source software that you've had for
40:37
Nemo and I think Megatron. And it's like they've been around for a long time. I
40:43
think Megatron has gone through many eras. I I have a note here. It's like these softwares have been going around
40:48
since like 2019 in some form and it's publicly we made our first public
40:54
release in 2019 but we started it earlier and it's um something that I found is that when I started doing like language
41:00
models so it was a late bloomer and we'll um transition to some career talk in a few minutes at hugging face like
41:06
Megatron had like a bad rep being very hard to use but now like three years later I hear from anyone that's founding
41:12
a new language modeling startup they're like just use Megatron Like do you pick up on things like this?
41:20
Is it just like random? But it's like be hard on it. You know, we're trying really hard to make Megatron easier to
41:26
use. It's difficult. Megatron is a complicated piece of technology. And you know, when we originally started
41:31
Megatron, the point was to show the community that you could make state-of-the-art large transformer
41:37
language models uh with Nvidia. I don't know if you recall, but um there was
41:43
some assertions by some other companies back in 2017 uh when the transformer was
41:49
invented that uh they could only be made uh without Nvidia. Um in fact, there
41:54
were statements to that effect on on official blog posts which I think got redacted later on. But um it was
42:00
important for Nvidia to show up and say we love language models, we love transformers, let's see what we could
42:06
do, you know, if we partitioned the work properly on lots of GPUs with an amazing interconnect. What kinds of models could
42:12
we train? And so that's where uh the Megatron project started. You know, I actually um came up with the name
42:18
Megatron. Um one of my proudest moments I suppose I I was thinking about I was like this is a really big transformer.
42:24
What's the biggest and baddest transformer? Oh, it's Megatron. So, that's, you know, where where the name came from. Um, but you'll think about
42:32
that. That had nothing to do with usability, right? Like I wasn't I wasn't thinking about like how do we make a
42:38
platform that's really easy for other people to use. I was just trying to show the world that like Nvidia systems could
42:43
be awesome for Transformers, you know? That was that was my goal. Over the years, you know, it has evolved. We have
42:49
a lot more um uh people trying to use Megatron. We got a lot of complaints about how hard it was to use. And then
42:55
we did a lot of work to try to improve the software engineering around Megatron. You know these days um
43:01
Megatron software engineering is actually shared between um about [clears throat] four different teams at
43:07
NVIDIA um and we have to coordinate that work very closely. That has also not
43:13
been easy. There has been times when um you know people wanted to fork Megatron
43:19
and then there were times when we like had to bring it back together and it's like look I know forking things is
43:24
always tempting but look better together it's better for all of us to to keep working together and so um I feel like
43:31
Megatron uh and especially Megatron core which is like a subset of Megatron that's like especially protected and we
43:38
try to put more software engineering into that um that that has uh gotten dramatically better um since we started
43:45
paying more attention to it as a company. Um are we done yet? No, there's
43:50
a lot a lot a lot more work. A bas a basic question is is Megatron or Megatron Core like this is what Neatron
43:58
is trained on and also and it's also something that many of the hottest like
44:03
AI startups are training their models on. I would guess that there's nothing else that does that. So I could
44:09
summarize why it's so hard. Well, you know, there's a there's a lot of other great frameworks out there. Megatron is
44:15
not the only one. Um uh and um you know, we're happy about that. Nvidia doesn't
44:20
need to control uh this space. What we what we do want to do is make sure that we're putting our products forward in
44:25
the best light, you know, and it's a challenging problem. We've got so many things going on with um with uh
44:32
precision and uh you know the networking like those those questions like the
44:38
software is so complicated. Um these days, you know, we're uh pre-training our um Neotron 3 um Super and Ultra
44:46
models using FP4, um which is a thing that, you know, h hasn't been done
44:52
publicly anyway. um and something that, you know, we're pretty excited about because um our GPUs um have really
45:00
awesome FP4 throughput, but obviously the numerical challenges of like trying to train a state-of-the-art language
45:06
model using uh 4bits uh is non-trivial. So like you know all of that work has to
45:13
go into Megatron into Transformer Engine uh which is another open source project that Megatron relies on and you know um
45:20
coordinating all of that um making sure that you know we can actually deliver the benefits of NVIDIA systems to people
45:25
that are trying to make state-of-the-art models that's really really important to us and you know of the 500 or so people
45:31
working on Megatron like a pretty good fraction or on Neotron a pretty good fraction of them are working on these
45:37
kinds of systems issues right because Nvidia at its core is a systems company.
45:42
Um, and Megatron Neatron's first job really is um, about systems, you know,
45:47
and and um, so we we we care we care deeply about that. Yeah. I mean, from my perspective, I was
45:52
at Hugging Face before AI2 and Hugging Face is like the best company at doing public work, but also and switching to
45:59
AI2 and focusing on like we're focused on the output artifact the most. seeing the different type like it's such a
46:05
different type of work going from you're trying to build a tool that's good for training models to build a tool that's
46:10
good for everybody else and whatever heck use case they are to do both is like I'm I'm happy that
46:17
AI2's repos aren't that popular in terms of open source adoption because we can't
46:23
handle it we just can't it's like so hard because it's people it's like it ends up being researchers that are
46:28
supporting it and we don't have the ability to scale the organization structure So, I just think like that's a that's a
46:36
very fun turnaround for me to think of all these things happening at once. Yeah. Well, thanks thanks for noticing
46:41
we're putting effort in. I would say Megatron is still not nearly as user friendly as hugging face libraries.
46:47
Hugging face libraries are legendary and um I admire the work they've done to
46:53
make the community so productive. um people, you know, are able to get so
46:58
much research done uh thanks to the work that, you know, Hugging Face has put into to their library. So, um you know,
47:04
my hats off to them as well. Yeah. One of my hot takes, you don't have to reply, is that Hugging Face and Nvidia have been very good partners. And
47:10
it's like bringing that hugging face culture to the Nvidia stuff would be so good. It's just so hard. So, I I don't
47:16
know how that would work, but we're trying, you know, and uh you know, it is it is challenging. Nvidia is
47:22
always a company that um is going to prioritize speed uh like hardware speed above
47:30
really anything else because that's like who we are. I am always trying to make the case that developer speed is
47:36
important too, right? It's like there's different ways of thinking about speed. Um and it is definitely the case that a
47:44
lot of NVIDIA's software um is so cumbersome to use that um you know uh
47:51
people can't get the actual hardware speed as fast as it should be because they just give up you know they just
47:57
don't don't even figure out how to use that. So um I think Nvidia is making strides there. Um, I think the the the
48:04
company is is understanding more deeply how important developer experience is and I I hope we continue to push that so
48:10
that the benefits of all of the systems technology that Nvidia works so hard on can be more widely used. Um, but at the
48:16
same time, you know, there is going to be a tension between those things, it's it's not going to go away. And um, you
48:22
know, to a certain extent, I think that's just uh life on planet Earth. It is. Um, I think you're you're doing a
48:28
good job. I'm going to kind of shift gears in this interview. So I've in becoming more back in language in
48:34
becoming a person that works in language models I've seen your name more and more time. I was like Brian Kenzar like where
48:39
have I seen this? And then I went and did the research of the Berkeley PhD in it says April of 2021 you gave a
48:45
Berkeley Eekes colloquium um titled applications of deep learning in graphics conversational AI and systems
48:50
design. I'm not even going to posit that I actually went, but that's definitely where I remembered the name from in grad
48:56
school. And we both have backgrounds that aren't traditionally in AI and end
49:02
up working in language models. I just wonder like what have you learned from
49:08
your path through Nvidia into what like people should be thinking about with AI
49:14
or open models today? This could be career reflections like like technical
49:20
reflections. I just think that there's there are actually a lot of people that come from all over the like STEM field
49:27
to work in AI. So giving it space to think about is useful even if it's just like it was the
49:34
big problem and I wanted to go solve it. Well, I think you know
49:41
I've I've had a lot of uh opportunity and a lot of luck uh in my career. Um, I
49:47
think in hindsight it seems like an extraordinarily lucky thing that, you know, I I did my first internship at
49:54
NVIDIA in 2008 and I was like building machine learning models on the GPU and I
50:00
I went to Nvidia and and nobody else was really doing that and I was like, hey, like we should have more people doing
50:06
machine learning on the GPU. I think this could be an opportunity. And um, you know, it took a few years for for me
50:12
to to make any headway. um uh Nvidia didn't really want to listen to me. I
50:17
was a brand new PhD. I was in the research organization which is very independent but you know sometimes
50:23
struggles to um change the way that the you know the bigger company thinks about things and um and yet I just had this
50:33
conviction, you know, I just was following my my heart about what do I think is going to be important? What do
50:39
I think could really change the world? And um that has been I think the the
50:45
thread that has taken me through my whole career is that I'm constantly trying to refine my beliefs about what
50:51
matters and then um um hold to them. And um that I don't know how helpful it is
50:59
to say that, but um I feel like sometimes people um you know tend to to
51:05
follow the whatever the thing is that people are talking about on Twitter. And like I've I've done a lot of unpopular
51:11
things um during my career because I believed in them. You know, I remember I
51:16
published my first um paper in 2008 on at ICML on um training support vector
51:23
machines on the GPU. And I actually had somebody at the conference. It was in Helsinki um at at dinner. You know, we
51:29
were all telling each other what we're doing. And and and I was like, "Yeah, I want to help people train bigger models on bigger data sets with GPUs." And and
51:36
I had, you know, a couple people just say, "Well, why are you here at ICML? That just doesn't really feel like a
51:42
good thing for us." And in 2008, ICML was mainly about um new mathematical
51:49
frameworks for thinking about data. And um you know, maybe if you trained a
51:54
model at all, you would train one on your laptop. You know, that was the state of machine learning in 2008. So
52:00
for somebody to come in and say I think I want to focus on like parallel computing, new kinds of hardware for
52:06
machine learning, programming frameworks for machine learning so that you know we more people can try um inventing new
52:12
models on on complicated machines with a lot more compute throughput on bigger data sets. That was like an unpopular
52:20
thing at least it felt very unpopular. or I felt very marginalized at the time by the community, but I believed in it.
52:27
You know, I just felt like look, technology like I I have this sense of like where do I think technolog is
52:33
going? I knew that um traditional computing uh was running out of steam.
52:39
You know, I had I had done a few internships at Intel and I was trying to help Intel make processors that ran at
52:45
like 10 gigahertz back in 2001. And you know, it was like clear that they were
52:52
running into a wall. And I was thinking, okay, so if the the compute hardware is going to have to be different, it's
52:58
going to be more restricted. It's not going to be able to be so general purpose in order to get speed, what kinds of applications are going to have
53:05
like an infinite need for more computing? And I thought, well, machine learning um and AI that that could
53:12
really change the world if it ever actually worked. But, you know, but you know, back then it back then it it kind
53:17
of worked inside of Google. Outside of Google it kind of didn't work. Um and so um so I had kind of these signals like
53:24
it was possible but it was hard. It was a little weird. It was a little niche. I was a little bit caught in between different fields like the the systems
53:31
people didn't think I was systems enough and the machine learning people didn't think I was machine learning enough. But I believed in what I was doing and I
53:38
found a way to keep following that belief and you know ultimately um it was
53:43
very rewarding when all of a sudden Nvidia decided hey uh deep learning is changing the world what do we know about
53:49
deep learning and then it was like oh well Brian's been doing that for several years and he's written some libraries that we could turn into a product let's
53:56
go do that and you know so that all happened really quickly after many years of nothing happening you know and that
54:04
was really um obviously ly an amazing uh opportunity for me. Um, you know,
54:09
another thing that was important to me, I um I left NVIDIA in 2014 um to go work
54:15
at the Silicon Valley AI lab um at BU um with um a group of really talented
54:21
people including Andrew Ing and Daario Amade and Ani Hanoon and Adam Coats and
54:28
um you know this was a a really once in a-lifetime opportunity I think um for me
54:34
to learn some things that would have been hard for me to learn on my own. Um, you know, I I felt at the time at NVIDIA
54:41
that although I had this great um opportunity to help Nvidia become an AI
54:47
company and I was doing that and I was succeeding at that back in 2013 um 2014.
54:52
I I also felt like um I really wanted to learn from a broader community of people
54:58
applying um machine learning and AI to solve really important business problems. And um uh so uh going to work
55:07
at BYU really gave me that chance. Um and I was there for a couple years, learned a ton. Um very grateful to the
55:14
the team there, especially to Andrew Ing who um who who uh encouraged me to to to
55:20
join with him on that. Um and uh then you know I I ran into um uh limits of
55:27
what I could do uh in California working for a Chinese company. I was thinking about, you know, what should I do next?
55:33
And Jensen asked me to come back um and build an applied research lab uh at NVIDIA in 2016. Um and um I wasn't sure
55:42
like if that was a good idea. I thought uh Nvidia's already grown so much. You know, the the years from 2014 to 2016,
55:48
Nvidia actually grew a lot. Um these days you look back at it and you're like it was still really tiny. But but back
55:54
then I was like I don't know, maybe Nvidia's already tapped out. I don't know if you recall in 2016 there was already like 10 different companies
56:00
making GPU competitors, right? The TPU had already been out for a while. Um and
56:06
uh you know it it it wasn't clear um that uh Nvidia was was going to become
56:12
uh uh as large as it as it has. But I believed in the opportunity. I believed
56:19
in the people. Um, you know, one of the things I loved about Nvidia was that uh it's a very um uh stable organization.
56:27
So Jensen, he's been running it since he founded it in 1993. Uh my boss Jonah
56:32
Albin who's an absolutely extraordinary person um has been here for um you know
56:39
quite quite a long time almost since the very beginning of NVIDIA and these people uh a lot of the leadership at
56:45
NVIDIA um they love the work their heart is in the work Jensen and Jonah and many
56:51
other leaders at NVIDIA they don't need to be doing this right they they have um earned the right to go sit on a beach
56:57
and drink my ties all day but their heart is in the work and They work incredibly hard. Um, you know, the uh I
57:04
feel like if there was an Olympics for email, you know, um, uh, Jensen would get the gold medal. You know, like it's
57:11
it's unfathomable to me like how much information he's able to process. Um, and it's a skill that he's built up over
57:18
a long time running this company, but it's also a reflection of his commitment to the work. And I felt like working at
57:25
a place where we've got this very stable organization that loves the work that
57:30
really wants to change the world, you know, why why does why does Jensen get up in the morning? Well, it's this is
57:36
his chance to do something meaningful. I thought associating with these people, you know, I could do worse. I could I
57:42
think I could learn learn from this as well. So um so I came came to Nvidia and back then uh it was really hard to
57:48
explain to people why I was trying to build an AI lab inside of Nvidia. At the
57:54
time Nvidia wasn't doing very much AI and um uh so I had to kind of um develop
57:59
a vision for that and then explain it to people. Um that's ended up being a really good idea for me um as well. You
58:06
know the the lab I think has has really helped Nvidia. Um, you know, Megatron, I think, has has really shown the industry
58:12
like how valuable NVIDIA systems can be for language modeling, which is which is awesome. DLSS, you know, um, I'm
58:19
continuing to to to push DLSS forward. Very excited about making graphics, you know, uh, more efficient with AI. These
58:26
days, you know, 15 out of every 16 pixels a gamer sees are rendered by AI models that, you know, my team
58:32
developed. And that then makes the GPU 10 times more power efficient. this is a really exciting uh you know thing for me
58:39
to be involved with something that I've you know dreamed about for for years. So so that's the the kind of thing that
58:45
continues to push me forward is that I I have strong beliefs about what I think is possible where I think technology is
58:51
going and I'm willing to do things that are weird and unpopular. Um but you know
58:57
basically following my convictions um I'm very much always thinking about the people I'm working with the tribe you
59:03
know I think tribes matter enormously um like uh you know uh if if I so so back
59:11
when I was a grad student I was working on programming models for machine learning I joined the Python tribe there are other people that were in the
59:17
scholar tribe and the people that did their work in the scholar tribe trying to make programming models for machine
59:22
learning in like 2010 um you know that work although a lot of it was technically excellent didn't matter to
59:29
the community as much as the people who are in the Python tribe. It ended up and and you know it kind of sucks sometimes
59:34
that the world is tribal like this but it's just the case you know that like the people that you work with the community that you work with um has a
59:41
big impact on the problems you think about and then the the impact that your work has. So I think a lot about the
59:46
people u and the tribes um that that I'm collaborating with or that I'm part of.
59:51
Um, and uh, you know, that's that's kind of been the thread that has carried me through my career.
59:56
Yeah, thank thanks for sharing this full arc. I think you've said things that I tell people about in different
1:00:02
languages. And the first one, the early days, it seems like there can be space in between fields where people two
1:00:10
fields will have their way of describing things, but both of them are probably incomplete and there can be space there,
1:00:15
which is a lot of what I was doing transitioning from novel robots to modelbased RL where I like didn't sit in
1:00:22
the actual AI lab, but I started doing AI with my like total electrical engineering friends. And then the second
1:00:29
thing is like I wholeheartedly recommend this to people is like choose your work based on the people and people that
1:00:36
sincerely are in it for the what they want to do and a lot of beliefs you know think about it
1:00:43
what do you believe in and it's okay to change your mind you know but like figure out what is it that you believe
1:00:49
in ask yourself every day do I still believe in that if I do what next you know if I don't well what do I believe
1:00:54
in you know that's been really important to me I I think too many people end up
1:01:00
kind of just following trends. That's not usually helpful because uh the trends are too late. So if you want to
1:01:07
if you want to change the world, you need to be ahead of the trends and you need to know you know it trends I don't
1:01:15
think trends in computing are just fashion. I think there's truth that drives those trends. Not always but
1:01:21
often. You know it's just this is it's there's kind of an inevitable force of gravity. It just can be really hard to
1:01:26
par parse out the noise um and figure out what is the truth that is going to push the industry forward and how can
1:01:32
you push that with with it. You know, if you can join with that, you can accomplish great things. Yeah, I agree. I think in in building
1:01:38
language models, it's like you want to build a model that the community wants in six months. I think if you're building a model to compete with the
1:01:45
models that are already out, you're not going to keep up. And I think that it's like what is the
1:01:52
right thing is building open language models in six months and like where do you need to try to steer things is one
1:01:58
of the hardest problems that I think about. So I if if you want to close with any predictions where you see like open
1:02:05
models like if we're if you're going to be here at the end of 2026 if there's
1:02:10
anything you think will be far more obvious than it is today or any bets that you want to make. I think it's kind of a good place to to wrap. Well, uh,
1:02:19
predictions are always hard and I I don't feel like I'm very good, um, at at making predictions, but I am I feel like
1:02:25
I am good at identifying what I believe in. And what I believe in right now is
1:02:30
that, um, compute remains one of the fundamental challenges behind AI. It has
1:02:36
been that way for a very long time. Um, and I think it continues to be. I think as we find new ways to apply compute to
1:02:43
AI, we discover new forms of scaling laws that help AI become more useful
1:02:49
uh and therefore it becomes more widespread. So I'm going to keep thinking about compute. I continue to
1:02:56
believe that the fastest that that you know the the way to think about AI is
1:03:02
not just in terms of absolute intelligence but rather intelligence per second. you know, there's some sort of
1:03:08
normalization in there that um relates to how fast a model can think, how fast
1:03:13
a model can be trained um or post-trained, you know, that models that
1:03:19
um kind of incorporate this compute acceleration characteristic where they're thinking about intelligence per
1:03:26
unit time. Those are going to end up winning because um they end up getting trained on more data. They end up
1:03:31
getting post-trained with more cycles. they end up with more iterations during thinking when they're deployed. Um, and
1:03:38
you know, of course, if they happen to fit the hardware really well, u, whatever hardware that is, uh, then, you
1:03:45
know, that can have a pretty non-trivial effect on the intelligence as well. So, that's something that that I I really
1:03:51
believe in. Um, I really believe in AI as um an infrastructure. You know,
1:03:57
there's there's different ways of thinking about AI. Um uh I think some
1:04:03
people believe AI is um uh more like the singularity like once AGI has been
1:04:10
declared then the whole world is different forever and all humans have lost their jobs and you know there's a
1:04:17
lot of like there's a lot of things about AI that people believe that um I personally don't believe you know I I
1:04:25
believe first of all that intelligence is very multifaceted um that it is not easy to pin down that
1:04:32
as soon as we try to pin down intelligence we find that there's very many more forms of intelligence that
1:04:37
aren't covered by that. So, for example, a model that achieves gold uh medal
1:04:43
status on the International Math Olympiad, that's an extraordinary achievement, but it doesn't make me have
1:04:49
no job, right? Like I'm actually not solving math problems all day, even though like having the ability to solve
1:04:55
math problems is clearly very useful. And um you know, it's also the case that
1:05:01
um intelligence is is you know, is is kind of like um a potential energy. uh
1:05:07
it's not a kinetic energy right in order to transform uh intelligence into kinetic energy it needs to have a
1:05:13
platform it needs to be applied in the proper way um and um you know that is
1:05:18
why I believe in open models and open openly developed and deployed
1:05:23
intelligence I believe every company every organization has secrets that only they know they have special data they
1:05:29
have special ways of thinking about their problems their customers their solutions and they're going to know how
1:05:35
to apply AI uh better than anyone else. And so, um, AI as infrastructure, um,
1:05:41
that transforms companies, turbocharges them, allows them to take the things they know and multiply their impact.
1:05:47
That's something that I believe in more than AI as an event that one day when it
1:05:53
happens makes everyone obsolete. I don't I just don't believe in that. Um, you
1:05:58
know, I I often joke that like uh if for example the CEO uh were to retire at
1:06:05
some point and we needed to find a replacement um you know handing out an IQ test or or asking you know who has
1:06:12
the highest SAT score. Uh that would not be a very good way of finding a replacement. You know um intelligence is
1:06:20
just far too complex for that. And so um uh you know so this this these these
1:06:26
beliefs you know you can disagree with me about anything that I just said. I'm not not offended by that. I have a lot
1:06:31
of friends that do. Um uh but you know I'm asking myself well if if I believe
1:06:38
uh that that intelligence has these characteristics and that AI is going to change the world by turbocharging institutions that exist um and also
1:06:45
creating new new applications that we haven't even dreamed of yet. um rather than replacing um all humans then, you
1:06:53
know, how do I go about building that, you know, and um so that's that's kind of um the direction that I'm on right
1:06:59
now. Yeah, I love it. I agree. I agree that we're entering an interesting area where
1:07:04
the open models are taking so many different shapes and sizes and have so many different strengths and trade-offs that there can start to be interesting
1:07:11
interplay um as an ecosystem where there's just so many different things going on. And I think I like your idea
1:07:18
of potential energy and you have to build things that are kind of unclear of what it's like you have to build build
1:07:24
the energy in a way and you don't really know what the goal is but you have to do try to build these good models. So I I
1:07:30
appreciate it and yeah and then let people apply it. Let it let them make the kinetic energy happen.
1:07:35
I agree. Thanks for coming on. Thanks [snorts] so much for inviting me. It's been a great conversation.
1:07:40
Yeah.
