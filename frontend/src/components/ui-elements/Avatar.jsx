import React from "react";
import * as Avatar from "@radix-ui/react-avatar";
import styles from './Avatar.module.css'

const AvatarComponent = ({ src, alt, fallback, delayMs = 600 }) => (
    <Avatar.Root className={styles.AvatarRoot}>
        {src ? (
            <Avatar.Image className={styles.AvatarImage} src={src} alt={alt} />
        ) : null}
        <Avatar.Fallback className={styles.AvatarFallback} delayMs={delayMs}>
            {fallback}
        </Avatar.Fallback>
    </Avatar.Root>
);

export default AvatarComponent;
