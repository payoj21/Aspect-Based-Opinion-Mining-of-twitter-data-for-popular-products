import React, { Component } from "react";
import ReactDOM from "react-dom";

export default class SparkSearchBar extends Component {

	handleClick() {
		const searchRef = this.refs.search;
		const node = ReactDOM.findDOMNode(searchRef);
		this.props.fetchPositions(node.value);
	}

	render() {
		return (
			<div id="custom-search-input" className="col-md-offset-1">
				<div className="input-group col-md-12 ">
					<input
						ref="search"
						type="text"
						className="form-control input-lg"
						placeholder="Enter a product name"
						style={{background: "transparent",color:"white"}}
					/>
					<span className="input-group-btn">
						<button
							className="btn btn-info btn-lg"
							type="button"
							onClick={this.handleClick.bind(this)}
						>
							<i className="glyphicon glyphicon-search" />
						</button>
					</span>
				</div>
			</div>
		);
	}
}
