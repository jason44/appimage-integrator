#include <appimage/appimage.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define REGISTER_SUCCESS 0

bool register_appimage(const char *appimage_file);

/* for debug purposes only */
void appimage_read_files(const char *appimage_file);

void extract_icon(const char *appimage_file, const char *dest);

void extract_destop_file(const char *appimage_file, const char *dest);

//void extract_desktop_file(const char *appimage_file, char *filename, const char *dest);

bool register_appimage(const char *appimage_file) {
	if (!appimage_is_registered_in_system(appimage_file)) {
		if (appimage_register_in_system(appimage_file, true) != REGISTER_SUCCESS) {
			return 0;
		}
	}
	return 1;
}

void appimage_read_files(const char *appimage_file) {
	char **files = appimage_list_files(appimage_file);
	int i = 0;
	while (files[i]) {
		printf("%s\n", files[i]);
		i++;
	}
	appimage_string_list_free(files);
}

void extract_icon(const char *appimage_file, const char *dest) {
	appimage_extract_file_following_symlinks(appimage_file, ".DirIcon", dest);
}

void extract_desktop_file(const char *appimage_file, const char *dest) {
	char *src=  appimage_registered_desktop_file_path(appimage_file, NULL, true);
	size_t src_len = strlen(src);
	size_t dest_len =  strlen(dest);
	char *cmd = malloc(src_len + dest_len + 5);
	memcpy(cmd, "cp ", 3);
	memcpy(cmd+3, src, src_len);
	memset(cmd+3+src_len, ' ', 1);
	memcpy(cmd+4+src_len, dest, dest_len+1);
	memset(cmd+4+src_len+dest_len, 0, 1);
	printf("%s\n", cmd);
	system(cmd);
	free(cmd);
}


