import React, {Component} from 'react';
import * as actionCreators from "../store/actions/actions";
import {connect} from "react-redux";
import Row from "react-bootstrap/Row";
import Col from "react-bootstrap/Col";
import Tabs from "react-bootstrap/Tabs";
import Tab from "react-bootstrap/Tab";
import Container from "react-bootstrap/Container";
import InputGroup from "react-bootstrap/InputGroup";
import FormControl from "react-bootstrap/es/FormControl";
import Fade from "react-bootstrap/Fade";
import Form from "react-bootstrap/Form";
import Table from "react-bootstrap/Table";
import {local as Local} from "../auth.js"
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";

function ApplicationEmailModal(props) {
	console.log("modal. props: ", props);
	return (
		<Modal
			{...props}
			size="lg"
			aria-labelledby="contained-modal-title-vcenter"
			centered
		>
			<Modal.Header closeButton>
				<Modal.Title id="contained-modal-title-vcenter">
					Modal heading
				</Modal.Title>
			</Modal.Header>
			<Modal.Body>
				<h4>Centered Modal</h4>
				<p>
					Cras mattis consectetur purus sit amet fermentum. Cras justo odio,
					dapibus ac facilisis in, egestas eget quam. Morbi leo risus, porta ac
					consectetur ac, vestibulum at eros.
				</p>
			</Modal.Body>
			<Modal.Footer>
				<Button onClick={props.onHide}>Close</Button>
			</Modal.Footer>
		</Modal>
	);
};

class Application extends Component {

	constructor(props) {
		super(props);

		this.state = {
			theApplication: null,
			finalStatus: 'Pending',
			statusMessage: '',
			controlClasses: '',
			notes: '',
			amountApproved: '',
			itemsApproved: '',
			appType: '',
			appPending: '',
			appApproved: '',
			appDenied: '',
			notesSaved: false,
			validated: false,
			readyToSave: false,
			hasSaved: false,
			filesDirectory: null,
			userFiles: null,
			isReady: false,
			sendEmail: false,
			setModalShow: false,
			modalShow: false
		};

		this.setApplicationSoftStatus = this.setApplicationSoftStatus.bind(this);
		this.saveNotes = this.saveNotes.bind(this);
		this.fieldChangeHandler = this.fieldChangeHandler.bind(this);
		this.handleSubmit = this.handleSubmit.bind(this);
	}

	hideModal = () => {
		this.setState({
			...this.state,
			modalShow: false
		});
	};


	componentDidMount() {
		this.getSingleApp();
	}

	getFileName(f) {
		const pieces = f.split(/[\s/]+/);
		return pieces[pieces.length-1];
	}

	getDirName(f) {
		const pieces = f.split(/[\s/]+/);
		return pieces[pieces.length-2];
	}

	getSingleApp() {
		this.props.getSingleApplication(this.props.match.params.id).then(result => {
			const app = this.props.selectedApplication != null ? this.props.selectedApplication : "nothing to see";

			this.setState({
				...this.state,
				theApplication: this.props.singleApp,
				orgName: app.orgName,
				appType: app.sponsorship_type_select,
				controlClasses: app.sponsorship_type_select + " controls",
				notes: (app.notes != null) ? app.notes : "",
				amountApproved: (app.amountApproved !=null && app.amountApproved !== "0") ? app.amountApproved : "",
				itemsApproved: (app.itemsApproved !=null) ? app.itemsApproved : "",
				appPending: app.finalStatus === "Pending" ? "active appStatus pending" : "d-none appStatus pending",
				appApproved: app.finalStatus === "Approved" ? "active appStatus approved" : "d-none appStatus approved",
				appDenied: app.finalStatus === "Denied" ? "active appStatus denied" : "d-none appStatus denied",
				filesDirectory: app.has_files === 1 ? app.user_directory : null,
				userFiles: app.has_files === 1 ? app.user_files : null,
				isReady: true
			}, ()=> {
				this.validateForm();
			});
		});
	}

	fixDir(f, index) {
		return !Local ? f.replace("/web/www/html/", "") : f.replace("/Applications/MAMP/htdocs/midrivers-sponsorships-admin/public/userFiles/CTRodeo", "/userFiles/"+this.getDirName(f));
	}

	setApplicationSoftStatus(event, message, status) {
		event.preventDefault();
		if(this.state.validated || status === "Denied" || status === "Pending") {
			this.setState({
				...this.state,
				finalStatus: status,
				statusMessage: message,
				readyToSave: true,
				hasSaved: false,

			}, () => {

			});
		}
	}

	fieldChangeHandler = (event) => {
		const target = event.target;
		const value = target.value;
		const name = target.name;

		// only want numbers and decimals. no letters. Also have to allow for an empty value
		// or the regex will yell at you.
		if(name === "amountApproved") {
			const lastCharacter = value.slice(-1);
			const regexp = /^[0-9,.]+([0-9]+)?$/g;
			const result = (name === "amountApproved") ? regexp.test(lastCharacter) : true;

			if (result || value === "") {
				this.setState({
					...this.state,
					[name]: value,
					hasSaved: false
				}, this.validateForm);
			}
		} else {
			this.setState({
				...this.state,
				[name]: value,
				hasSaved: false
			}, this.validateForm);
		}

	};

	validateForm() {
		if(this.state.amountApproved.length > 0 || this.state.itemsApproved.length > 0) {
			this.setState({
				...this.state,
				validated: true,
				hasSaved: false
			});
		} else {
			this.setState({
				...this.state,
				validated: false,
				readyToSave: false,
				hasSaved: false
			});
		}
	}

	saveNotes(e) {
		e.preventDefault();
		this.props.saveNotes(this.props.match.params.id, this.state.notes);
	}

	handleSubmit(e) {
		e.preventDefault();
		if((this.state.validated && this.state.readyToSave) || (this.state.finalStatus === "Denied" || this.state.finalStatus === "Pending")) {
			const appId = this.props.match.params.id;
			const appStatus = this.convertStatusToInt(this.state.finalStatus);
			this.props.saveApplicationStatus(appId, appStatus, this.state.notes, this.state.appType, this.state.itemsApproved, this.state.amountApproved)
				.then(result => {
					const savedStatus = this.props.applicationSavedStatus;
					this.setState({
						...this.state,
						finalStatus: savedStatus.status,
						appPending: savedStatus.status === "Pending" ? "active appStatus pending" : "d-none appStatus pending",
						appApproved: savedStatus.status === "Approved" ? "active appStatus approved" : "d-none appStatus approved",
						appDenied: savedStatus.status === "Denied" ? "active appStatus denied" : "d-none appStatus denied",
						hasSaved: true,
						modalShow: this.state.statusMessage === "Email Followup"
					}, () => {

					});
				});
		}
	}

	confirmMessage() {
		if(this.state.readyToSave && !this.state.hasSaved) {
			return (
				<>
					<Fade>
						<div className={"submission-confirmation alert-warning" + (!this.state.hasSaved ? " show" : '')}>
							<p>You have marked this application as <span className="applicationStatus">{this.state.statusMessage}</span>.</p>
							<p>Click the Finish Application button to confirm this choice.</p>
						</div>
					</Fade>
				</>
			)
		} else if (this.state.readyToSave && this.state.hasSaved) {
			return (
				<>
					<Fade>
						<div className={"submission-confirmation alert-success" + (this.state.hasSaved ? " show" : '')}>
							<p>You have saved this application as <span className="applicationStatus">{this.state.statusMessage}</span>.</p>
							<p>You can click the Home button to return to the list of applications.</p>
						</div>
					</Fade>

				</>
			)
		}
	}

	convertStatusToInt(status) {
		switch (status) {
			case "Pending":
				return 0;
			case "Approved":
				return 1;
			case "Denied":
				return 2;
			default:
				return 0;
		}
	}

	render() {
		const confirmation = this.confirmMessage();
		let errorMessage = null;
		let message = 'Your are not logged in.';

		const userFiles = this.state.isReady && this.state.theApplication.user_files != null ? this.state.theApplication.user_files.map((f, index) => (
			<a key={index} href={"https://www.midrivers.com/"+this.fixDir(f, index)} target="_blank" rel="noopener noreferrer">{this.getFileName(f)}</a>
		)) : null;

		errorMessage = (
			<div className={"error"}>
				<Row>
					<Col>
						<div className="alert alert-danger" role="alert">
							<p>{message}</p>
						</div>
					</Col>
				</Row>
			</div>
		);

		let content = this.state.isReady ? (
			<>
				<section className="application-header text-left">
					<Row>
						<Col lg={6}>
							<h5 className="text-left">Sponsorship Request for:<br/> <span className="org_name_header"> {this.state.orgName}</span></h5>
						</Col>
						<Col lg={6}>
							<p className="approvalStatus text-md-right">Application Status:<br/>
								<span className={this.state.appPending}> Pending</span>
								<span className={this.state.appApproved}> Approved</span>
								<span className={this.state.appDenied }> Denied</span></p>
						</Col>
					</Row>
				</section>
				<Row>
					<Col>
						<Tabs defaultActiveKey="application" className="admin-tabs">
							<Tab eventKey="application" title={<span>Application</span>}>
								<Row>
									<Col>
										<h4>Organization Information</h4>
										<Table striped bordered hover size="sm" responsive id="pendingTable" className="text-left applicationTable singleApplicationTable">
											<thead>
											<tr>
												<th role="columnheader" className="">Questions</th>
												<th role="columnheader" className="">Answers</th>
											</tr>
											</thead>
											<tbody>
											<tr>
												<td>Are You requesting as an Organization or Individual?</td>
												<td data-id="org_or_indv" className="answer">Organization</td>
											</tr>
											<tr>
												<td>Organization Name</td>
												<td data-id="org_name" className="answer">{this.state.theApplication.org_name}</td>
											</tr>
											<tr>
												<td>Organization's Physical Address</td>
												<td className="answer">
													<span data-id="org_address">{this.state.theApplication.org_address}</span>
													<br/><span data-id="org_city">{this.state.theApplication.org_city}</span><span data-id="org_state">{this.state.theApplication.org_state}</span>, <span data-id="org_zip">{this.state.theApplication.org_zip}</span>
												</td>
											</tr>
											<tr>
												<td>Year Established</td>
												<td data-id="year_est" className="answer">{this.state.theApplication.org_year_est}</td>
											</tr>
											<tr>
												<td>Organization's Website URL</td>
												<td data-id="org_website" className="answer">{this.state.theApplication.org_website}</td>
											</tr>
											<tr>
												<td>Organization's Facebook Page</td>
												<td data-id="org_facebook" className="answer">{this.state.theApplication.org_facebook}</td>
											</tr>
											<tr>
												<td>Organization's Instagram Username</td>
												<td data-id="org_instagram" className="answer">{this.state.theApplication.org_instagram}</td>
											</tr>
											<tr>
												<td>Organization's Twitter Handle</td>
												<td data-id="org_twitter" className="answer">{this.state.theApplication.org_twitter}</td>
											</tr>
											</tbody>
										</Table>
									</Col>
								</Row>

								<Row className="row-push">
									<Col>
										<h4>Primary Contact Information</h4>
										<Table striped bordered hover size="sm" responsive id="pendingTable" className="text-left applicationTable singleApplicationTable">
											<thead>
											<tr>
												<th>Questions</th>
												<th>Answers</th>
											</tr>
											</thead>
											<tbody>
											<tr>
												<td>Primary Contact Name</td>
												<td data-id="primary_name" className="answer">{this.state.theApplication.primary_name}</td>
											</tr>
											<tr>
												<td>Primary Contact Email</td>
												<td data-id="primary_email" className="answer">{this.state.theApplication.primary_email}</td>
											</tr>
											<tr>
												<td>Primary Contact Phone</td>
												<td data-id="primary_phone" className="answer">{this.state.theApplication.primary_phone}</td>
											</tr>
											<tr>
												<td>Primary Contact Address</td>
												<td className="answer">
													<span data-id="primary_address">{this.state.theApplication.primary_address}</span>
													<br/>
													<span data-id="primary_city">{this.state.theApplication.primary_city}</span>
													<span data-id="primary_state">{this.state.theApplication.primary_state}</span>,
													<span data-id="primary_zip">{this.state.theApplication.primary_zip}</span>
												</td>
											</tr>
											<tr>
												<td>Title/Relationship to Organization/Individual</td>
												<td data-id="relationship" className="answer">{this.state.theApplication.relationship}</td>
											</tr>
											</tbody>
										</Table>
									</Col>
								</Row>


								<Row className="row-push">
									<Col>
										<h4>Event Information</h4>
										<Table striped bordered hover size="sm" responsive id="pendingTable" className="text-left applicationTable singleApplicationTable">
											<thead>
											<tr>
												<th>Questions</th>
												<th>Answers</th>
											</tr>
											</thead>
											<tbody>
											<tr>
												<td>What type of request are you making?</td>
												<td data-id="sponsorship_type_select" className="answer">{this.state.theApplication.sponsorship_type_select}</td>
											</tr>
											<tr>
												<td>Event/Project Name</td>
												<td data-id="event_name" className="answer">{this.state.theApplication.event_name}</td>
											</tr>
											<tr>
												<td>Event/Project Description</td>
												<td data-id="event_description" className="answer">{this.state.theApplication.event_description}</td>
											</tr>
											<tr className="monetary">
												<td>Amount Requested</td>
												<td data-id="amount_requested" className="answer">{this.state.theApplication.amount_requested}</td>
											</tr>
											<tr className="monetary">
												<td>Money Needed By</td>
												<td data-id="money_needed_by_date" className="answer">{this.state.theApplication.money_needed_by_date}</td>
											</tr>
											<tr>
												<td>Why are you seeking sponsorship?</td>
												<td data-id="why_seeking" className="answer">{this.state.theApplication.why_seeking}</td>
											</tr>
											<tr className="material">
												<td>Items Requested</td>
												<td data-id="items_requested" className="answer">{this.state.theApplication.items_requested}</td>
											</tr>
											<tr className="material">
												<td>Items Needed By</td>
												<td data-id="items_quantity" className="answer">{this.state.theApplication.items_quantity}</td>
											</tr>
											<tr>
												<td>Purpose of Sponsorship</td>
												<td data-id="sponsorship_purpose" className="answer">{this.state.theApplication.sponsorship_purpose}</td>
											</tr>
											<tr>
												<td>Benefits available with sponsorship</td>
												<td data-id="benefits" className="answer">{this.state.theApplication.benefits}</td>
											</tr>
											<tr>
												<td>Advertising Dates</td>
												<td data-id="advertisingDate" className="answer">{this.state.theApplication.advertisingDate}</td>
											</tr>
											<tr>
												<td>Audience Reached with Sponsorship</td>
												<td data-id="audience_reached" className="answer">{this.state.theApplication.audience_reached}</td>
											</tr>
											<tr>
												<td>Describe in Detail any advertising materials needed from Mid-Rivers</td>
												<td data-id="advertising_details" className="answer">{this.state.theApplication.advertising_details}</td>
											</tr>
											<tr>
												<td>Referred By</td>
												<td data-id="referred_by" className="answer">{this.state.theApplication.referred_by}</td>
											</tr>
											<tr>
												<td>Any additional information or notes you would like add?</td>
												<td data-id="additional_info" className="answer">{this.state.theApplication.additional_info}</td>
											</tr>
											<tr>
												<td>Files</td>
												<td data-id="file_list" className="answer userFiles">{userFiles}</td>
											</tr>
											</tbody>
										</Table>
									</Col>
								</Row>
							</Tab>

							<Tab eventKey="functions" title={<span>Admin Functions</span>}>
								<section className={this.state.controlClasses}>
									<Form>
										<Row>
											<Col lg={6}>
												<div className="note-wrap">
													<p className="lead">Reviewer Notes</p>
													<FormControl
														as="textarea" aria-label="notes" data-id="notes" id="notes" name="notes" rows="6"
														onChange={this.fieldChangeHandler} value={this.state.notes} />
												</div>
											</Col>

											<Col lg={6}>
												<div className="monetary">
													<p className="lead">Monetary Options</p>
													<InputGroup className="">
														<InputGroup.Prepend>
															<InputGroup.Text id="amount-approved">$</InputGroup.Text>
														</InputGroup.Prepend>
														<FormControl
															placeholder="Amount Approved" aria-label="Amount Approved" aria-describedby="amount-approved"
															name="amountApproved" value={this.state.amountApproved}
															onChange={this.fieldChangeHandler}
														/>
													</InputGroup>
													<p className="small text-muted">Numbers and decimals only.</p>
												</div>
												<div className="material">
													<p className="lead">Material Items Approved:</p>
													<FormControl
														as="textarea" aria-label="items" name="itemsApproved" id="itemsApproved"
														rows="1" onChange={this.fieldChangeHandler}
														value={this.state.itemsApproved}/>
													<p className="small text-muted">List all items separated with a comma.</p>
												</div>
												{confirmation}
											</Col>
										</Row>

										<Row>
											<Col lg={6}>
												<div className="button-wrap">
													<div className="wrap">
														<button onClick={(e) => this.saveNotes(e)} data-status="Pending" className={"btn save-notes approvalStatus" + (this.state.notes.length > 0 ? "" : " disabled")}>Save Notes</button>
														<button onClick={(e) => this.setApplicationSoftStatus(e,"Needing Review", "Pending")} data-status="Pending" className="btn review approvalStatus">Needs Review</button>
														<a href={"mailto:"+this.state.theApplication.primary_email} onClick={(e) => this.setApplicationSoftStatus(e,"Email Followup", "Pending")} data-status="Pending" className="btn email approvalStatus">Email Followup</a>
														<a className="mailto" href={"mailto:"+this.state.theApplication.primary_email} ref={"mailLink"}>Mail</a>
													</div>
													<div className="wrap">
														<button onClick={(e) => this.setApplicationSoftStatus(e,"Approved", "Approved")} data-status="Approved" className={"btn approve approvalStatus" + (this.state.validated ? "" : " disabled")}>Approve</button>
														<button onClick={(e) => this.setApplicationSoftStatus(e,"Denied", "Denied")} data-status="Denied" name="denied" className="btn deny approvalStatus">Deny</button>
													</div>
												</div>
											</Col>

											<Col lg={6}>
												<div className="button-wrap finish">
													<div className="wrap">
														<button data-status="" onClick={(e) => this.handleSubmit(e)} className={"btn finish approvalStatus" + (this.state.readyToSave ? "" : " disabled")}>Finish Application</button>
													</div>
												</div>
											</Col>
										</Row>
									</Form>
								</section>
							</Tab>
						</Tabs>
					</Col>
				</Row>
				<ApplicationEmailModal show={this.state.modalShow} onHide={() => {
					this.hideModal();
				}}/>
			</>
		) : null;

		if (!this.props.loggedIn) {
			content = errorMessage;
		}

		return (
			<Container>
				{content}
			</Container>
		);
	}
}

const mapStateToProps = state => {
	return {
		selectedApplication: state.selectedApplication,
		notesSaved: state.notes,
		applicationSavedStatus: state.applicationSavedStatus,
		applicationFinalStatus: state.applicationFinalStatus,
		loggedIn: state.loggedIn,
		singleApp: state.singleApplication
	}
};

const mapDispatchToProps = dispatch => {
	return {
		getSingleApplication: (applicationId) => dispatch(actionCreators.getSingleApplication(applicationId)),
		saveNotes: (id, notes) => dispatch(actionCreators.saveNotesToDB(id, notes)),
		saveApplicationStatus: (id, status, notes, appType, items, money ) => dispatch(actionCreators.saveApplicationStatus(id, status, notes, appType, items, money)),
		applicationFinalStatus: (status) => dispatch(actionCreators.saveNotesToDB(status))
	}
};

export default connect(mapStateToProps, mapDispatchToProps)(Application);