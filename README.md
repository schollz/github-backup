# github-backup

As of [December, 2018](https://github.blog/2018-12-19-download-your-data/) you can download all your GitHub data with the click of a button. However, as of August 2020, this still won't work if you have too many repositories and will result in a unicorn page:

![Death screen](https://user-images.githubusercontent.com/6550035/90820186-d52b6300-e2e5-11ea-9849-f06dc3377154.png)

When I emailed support, they suggested to use [the official migration API](https://docs.github.com/en/rest/reference/migrations) to do the download.

So I wrote this python script to do just that. You can simply backup all the repos from Github using the official API.

## Usage

Before you start, make sure to get a `<secret token>` that has admin priveleges, see [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).

```
> python -m pip install loguru click requests tqdm
> wget https://raw.githubusercontent.com/schollz/github-backup/master/github-backup.py
> python github-backup.py --user schollz --token <secret token>
```


## License

MIT
