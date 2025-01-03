# SoundBase CLI App

**SoundBase** is a command-line application designed to help you manage a media database. It allows users to add, update, delete, and search for media entries and sources, making it easier to organize and retrieve music, video, and other media files. The app stores all media content in a centralized SQLite database (`soundbase.db`), providing a simple and efficient way to handle media across different sources, such as YouTube and other platforms.

Personally, I use SoundBase to manage all my media content. Whenever I plan to switch to a new system, I rely on the `download` command to save my `soundbase.db` file to the `~/Downloads` directory. Once I have set up the app on my new machine, I can simply copy the `soundbase.db` file to the `~/.soundbase/soundbase.db` location, ensuring a seamless transition with all my media content intact and ready to use.



**GitHub Repository:** [SoundBase GitHub Repository](https://github.com/indrajit912/SoundBase.git)

**Copyright:** © 2025 [Indrajit Ghosh](https://indrajitghosh.onrender.com). All rights reserved.


## Installation

To install SoundBase, run the following terminal command:

```bash
curl -o ~/Downloads/install_soundbase.sh https://raw.githubusercontent.com/indrajit912/SoundBase/master/scripts/install_soundbase.sh && chmod +x ~/Downloads/install_soundbase.sh && ~/Downloads/install_soundbase.sh
```

This will download and execute the installation script, setting up the SoundBase application on your system.

### Uninstallation

To uninstall SoundBase, run the following terminal command:

```bash
curl -o ~/Downloads/uninstall_soundbase.sh https://raw.githubusercontent.com/indrajit912/SoundBase/master/scripts/uninstall_soundbase.sh && chmod +x ~/Downloads/uninstall_soundbase.sh && ~/Downloads/uninstall_soundbase.sh
```

This will download and execute the uninstallation script to remove SoundBase from your system.

## Command List

### `init`
Initialize the SoundBase database. Creates a new database and adds a predefined source (YouTube) if the database doesn't already exist.

```bash
$ soundbase init
```

### `add`
Add a new media entry (such as a music or video file) to the database. You must provide the media URL.

```bash
$ soundbase add --url "https://example.com/media/video1.mp4"
```

### `add-source`
Add a new source (such as a music or video website) to the SoundBase database. If the source already exists, no new source will be created.

```bash
$ soundbase add_source --name "YouTube" --url "https://youtube.com"
```

### `list`
List all media entries or all sources in the database. Use flags to specify what to list:

- `-m` or `--media`: List all media entries.
- `-s` or `--sources`: List all sources.

```bash
$ soundbase list --media
$ soundbase list --sources
```

### `search`
Search for media or sources in the database.

- `media`: Search for media entries by filters like title, URL, or source ID.
- `source`: Search for sources by filters like name, base URL, or source ID.

```bash
$ soundbase search media --title "example title"
$ soundbase search media --url "http://example.com"
$ soundbase search source --base_url "http://youtube.com"
```

### `update`
Update media or source information in the database.

- `media`: Update media details by ID (e.g., title, URL, or source ID).
- `source`: Update source information.

Examples:

```bash
$ soundbase update media --media_id <media_id> --url <new_url>
$ soundbase update source --id <source_id> --name <new_name> --base_url <new_url>
```

### `del`
Delete a source or media entry from the database. Specify whether you want to delete a media entry or a source using the appropriate flag (`--media` or `--source`).

```bash
$ soundbase del --media
$ soundbase del --source
```

### `download`
Download media or the entire SoundBase database to a specified directory.

- `media`: Download media by ID or URL.
- `db`: Download the SoundBase database.

Examples:

```bash
$ soundbase download media --id <media_id>
$ soundbase download db --download_dir "/path/to/directory"
```

### `local`
Manage local system-related information such as username and media directory.

- `info`: Display current system information.
- `update`: Update system-related information like username and media directory.

Examples:

```bash
$ soundbase local info
$ soundbase local update --username new_username
$ soundbase local update --media_dir /new/path/to/media
```


## Usage

After installation, you can run the application directly from the command line:

```bash
soundbase <command> [options]
```

Refer to the individual commands for specific options and usage.


## License

SoundBase is licensed under the [MIT License](./LICENSE).
