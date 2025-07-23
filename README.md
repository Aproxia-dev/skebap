# Skebap

A simple Pastebin clone written in FastAPI, Python, Jinja and HTMX.

## Foreword / Background

I started this project in fall of 2023 and finished it in spring of 2024 as a high school graduation project, and I've been hiding it since because I simply felt that it wasn't good enough.

Given the fact that it was made during some of the most miserable years of my life, I didn't have enough time and energy to dedicate to the project and turn it into something genuinely worthwhile.

With that said, now that it's been over a year since I've graduated, and I'm actually working on software in a proper corporate environment and getting respect for it while largely using the same exact stack and design principles, I have come to the conclusion that what I've made really wasn't as stupid and useless as I initially thought, and I've decided to stop hiding it, as given the context, I believe that this project isn't something to feel ashamed of.

I would like to thank [`Octelly`](https://github.com/Octelly) for helping me out with this project as I feel like I really wouldn't've been able to steer the wheel alone given the circumstances.

And I would also like to publically tell my high school IT teacher to eat shit for the sheer amount of bullshit he made me go through during my time spent working on this project, including but not limited to:
- Telling me I can use whatever stack I wanted instead of sticking with the recommended LAMP stack only to yell at me every time I made it known that I actually rolled my own
- Constantly insulting me for doing things *the modern way* and using a proper deployment pipeline with Git and Docker instead of hosting it on what's essentially [the czech equivalent of godaddy](https://endora.cz) and pushing to prod via FTP directly
- Harassing me for being "lazy" when I was just on medication that was messing with me horribly
- Continuing to fuck me over and holding my grades hostage while I was locked up in a psych ward

Fuck you too, and I hope someone who actually has authority finally sees through your bullshit soon.

### Conclusion

I feel like this project helped me grow immensely, as it was not only my first proper full-stack project where I was able to show that I am genuinely interested in the space, but it also taught me a lot about standing up for myself and dealing with people with fragile egos. I am mostly just happy to say that this chapter of my life is finally behind me, but I still stand by all of the decisions I've made during it.

If I was to get the same assignment now with the things I've learned since, I would've dropped the medication I was on at the time, replaced HTMX with Svelte or React, and probably built like a Twitter Clone instead.

## Running

This project is deployed using Docker, it is the only runtime dependency on the host system.

``docker compose up -d --build``
