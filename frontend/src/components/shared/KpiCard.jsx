import styles from './KpiCard.module.css';
import tinycolor from 'tinycolor2';

const KpiCard = ({ title, Icon, color, buttonTitle, kpiValue, onClick = () => { } }) => {
    const lighterColor = tinycolor(color).lighten(35).toString();
    return (
        <div className={styles.KpiContainer}>
            <div className={styles.TitleContainer}>
                <div className={styles.Title}>
                    {title}
                </div>

                <div className={styles.IconContainer} style={{ background: lighterColor }}>
                    {Icon && <Icon color={color} />}
                </div>
            </div>

            <p className={styles.KpiValue}>{kpiValue}</p>
            <button className={styles.Button} style={{ background: color }} onClick={onClick}>{buttonTitle}</button>
        </div>
    )
}

export default KpiCard;