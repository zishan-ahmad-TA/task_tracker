import styles from './ListCard.module.css';
import { MdEdit } from "react-icons/md";
import { MdDelete } from "react-icons/md";
import { FaCircle } from "react-icons/fa";
import TooltipComponent from '../ui-elements/Tooltip';

const ListCard = ({
    label = "", value = "",
    status = "",
    showStatusIcon = true, isWorkItems = true, isDelete = true,
    listClickable = false,
    onDeleteIconClick = () => { },
    onEditIconClick = () => { },
    onLabelClick = () => { }
}) => {
    const statusColor = status === "Closed" ? "#E59178" : "#82C468";

    return (
        <div className={styles.ListCardContainer}>
            <div className={styles.CardText}>
                <div
                    className={styles.CardTitle}
                    style={{ cursor: listClickable ? 'pointer' : 'default' }}
                    onClick={onLabelClick}
                >

                    {label}
                </div>

                <div className={styles.CardDesc}>
                    {value}
                </div>
            </div>
            <div style={{ display: 'flex', gap: '15px' }}>
                <div className={styles.CardStatus}>
                    {showStatusIcon && <FaCircle size='10px' color={statusColor} />}
                    {status}
                </div>
                <div className={styles.CardIconContainer}>
                    {isWorkItems &&
                        <>
                            <TooltipComponent tooltipText="Edit">
                                <div onClick={onEditIconClick}>
                                    <MdEdit size='20px' style={{ cursor: 'pointer' }} />
                                </div>
                            </TooltipComponent>

                            {isDelete &&
                                <TooltipComponent tooltipText="Delete">
                                    <div onClick={onDeleteIconClick}>
                                        <MdDelete size='20px' color='#ff4d3d' style={{ cursor: 'pointer' }} />
                                    </div>
                                </TooltipComponent>
                            }
                        </>
                    }
                </div>
            </div>
        </div >
    )
}

export default ListCard;
