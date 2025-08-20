import React, {useState} from "react";
import {DataGrid} from "@mui/x-data-grid";
import {
    Dialog,
    DialogTitle,
    DialogContent,
    IconButton,
    Typography,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

const ResultsTable = ({rows}) => {
    const [open, setOpen] = useState(false);
    const [selectedData, setSelectedData] = useState(null);

    const columns = [
        {field: "id", headerName: "Result ID", flex: 1},
        {field: "run_id", headerName: "Run ID", flex: 1},
        {field: "created_at", headerName: "Created At", flex: 1},
        {
            field: "data",
            headerName: "Data",
            flex: 3,
            renderCell: (params) => (
                <div
                    style={{
                        cursor: "pointer",
                        width: "100%",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                    }}
                    onClick={() => {
                        setSelectedData(params.value);
                        setOpen(true);
                    }}
                >
                    {JSON.stringify(params.value)?.slice(0, 80)}...
                </div>
            ),
        },
    ];

    return (
        <div style={{height: "calc(100vh - 200px)", width: "100%"}}>
            <DataGrid
                rows={rows}
                columns={columns}
                getRowId={(row) => row.id}
                pageSize={10}
                rowsPerPageOptions={[10, 25, 50]}
                disableSelectionOnClick
            />

            {/* Popup JSON Viewer */}
            <Dialog
                open={open}
                onClose={() => setOpen(false)}
                maxWidth="md"
                fullWidth
            >
                <DialogTitle>
                    Result Data
                    <IconButton
                        aria-label="close"
                        onClick={() => setOpen(false)}
                        sx={{
                            position: "absolute",
                            right: 8,
                            top: 8,
                            color: (theme) => theme.palette.grey[500],
                        }}
                    >
                        <CloseIcon/>
                    </IconButton>
                </DialogTitle>
                <DialogContent
                    dividers
                    sx={{
                        maxHeight: "70vh",    // 👈 popup yüksekliği sınırlı
                        overflowY: "auto",    // 👈 scroll bar ekledik
                    }}
                >
                    {selectedData ? (
                        <Typography
                            component="pre"
                            sx={{
                                whiteSpace: "pre-wrap",
                                fontSize: "0.85rem",
                            }}
                        >
                            {JSON.stringify(selectedData, null, 2)}
                        </Typography>
                    ) : (
                        <Typography>No data selected</Typography>
                    )}
                </DialogContent>
            </Dialog>

        </div>
    );
};

export default ResultsTable;
